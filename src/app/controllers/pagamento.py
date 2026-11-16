"""Pagamento simulado do pedido."""

from __future__ import annotations

from typing import Annotated, Any, cast

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import Response
from sqlalchemy import select, update
from sqlalchemy.engine import CursorResult

from app.controllers.comum import (
    Sessao,
    avisar,
    avisar_codigo,
    redirecionar,
    renderizar,
    renderizar_form,
)
from app.core.acesso import exigir_usuario
from app.core.csrf import validar_csrf
from app.core.problemas import ErroAplicacao
from app.models import (
    Pedido,
    Produto,
    StatusPagamento,
    Usuario,
)
from app.services.operacoes import registrar_historico
from app.services.pagamento import simular

router = APIRouter(dependencies=[Depends(validar_csrf)])


def _pedido_do_cliente(banco: Sessao, pedido_id: int, usuario_id: int) -> Pedido:
    pedido = banco.scalar(select(Pedido).where(Pedido.id == pedido_id))
    if pedido is None or pedido.cliente_id != usuario_id:
        raise ErroAplicacao("ERR-PED-001")
    return pedido


@router.get("/pedidos/{pedido_id}/pagamento")
def pagamento_get(
    request: Request,
    banco: Sessao,
    pedido_id: int,
    usuario: Annotated[Usuario, Depends(exigir_usuario)],
) -> Response:
    pedido = _pedido_do_cliente(banco, pedido_id, usuario.id)
    if pedido.pagamento is None:
        raise ErroAplicacao("ERR-PED-004")
    if pedido.pagamento.status == StatusPagamento.APROVADO:
        avisar_codigo(request, "ERR-PAG-003", tipo="info")
        return redirecionar(f"/pedidos/{pedido.id}")
    return renderizar(request, "pagamento/form.html", pedido=pedido)


@router.post("/pedidos/{pedido_id}/pagamento")
def pagamento_post(
    request: Request,
    banco: Sessao,
    pedido_id: int,
    usuario: Annotated[Usuario, Depends(exigir_usuario)],
    metodo: Annotated[str, Form()] = "",
    numero_cartao: Annotated[str, Form()] = "",
) -> Response:
    pedido = banco.scalar(select(Pedido).where(Pedido.id == pedido_id).with_for_update())
    if pedido is None or pedido.cliente_id != usuario.id:
        raise ErroAplicacao("ERR-PED-001")
    pagamento = pedido.pagamento
    if pagamento is None:
        raise ErroAplicacao("ERR-PED-004")
    if pagamento.status == StatusPagamento.APROVADO:
        raise ErroAplicacao("ERR-PAG-003")

    try:
        resultado = simular(metodo, numero_cartao)
    except ErroAplicacao as erro:
        return renderizar_form(request, "pagamento/form.html", erro=erro, pedido=pedido)

    pagamento.metodo = metodo
    if not resultado.aprovado:
        pagamento.status = StatusPagamento.RECUSADO
        pagamento.cartao_ultimos4 = resultado.ultimos4
        banco.commit()
        avisar_codigo(request, "ERR-PAG-001")
        return redirecionar(f"/pedidos/{pedido.id}/pagamento")

    for item in pedido.itens:
        atualizacao = cast(
            CursorResult[Any],
            banco.execute(
                update(Produto)
                .where(
                    Produto.id == item.produto_id,
                    Produto.estoque >= item.quantidade,
                )
                .values(estoque=Produto.estoque - item.quantidade)
                .execution_options(synchronize_session=False)
            ),
        )
        if atualizacao.rowcount != 1:
            banco.rollback()
            raise ErroAplicacao(
                "ERR-PAG-004",
                detalhe=f"Estoque insuficiente para {item.nome_produto}.",
            )

    pagamento.status = StatusPagamento.APROVADO
    pagamento.valor = pedido.total
    pagamento.cartao_ultimos4 = resultado.ultimos4
    pagamento.codigo_autorizacao = resultado.codigo
    registrar_historico(
        banco,
        pedido.id,
        pedido.status,
        usuario.id,
        f"Pagamento aprovado via {metodo}.",
    )
    banco.commit()
    avisar(request, "Pagamento aprovado. Seu pedido entrou na fila.")
    return redirecionar(f"/pedidos/{pedido.id}")
