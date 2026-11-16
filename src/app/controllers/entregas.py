"""Área do entregador: entregas atribuídas e confirmação."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.responses import Response
from sqlalchemy import select

from app.controllers.comum import Sessao, avisar, redirecionar, renderizar
from app.core.acesso import exigir_papel, exigir_usuario
from app.core.csrf import validar_csrf
from app.core.problemas import ErroAplicacao
from app.models import Papel, Pedido, StatusPedido, Usuario
from app.services.operacoes import registrar_historico

router = APIRouter(
    prefix="/entregas",
    dependencies=[Depends(validar_csrf), Depends(exigir_papel(Papel.ENTREGADOR))],
)


@router.get("")
def listar_entregas(
    request: Request,
    banco: Sessao,
    usuario: Annotated[Usuario, Depends(exigir_usuario)],
) -> Response:
    pedidos = list(
        banco.scalars(
            select(Pedido)
            .where(
                Pedido.entregador_id == usuario.id,
                Pedido.status == StatusPedido.SAIU_ENTREGA,
            )
            .order_by(Pedido.criado_em)
        ).all()
    )
    return renderizar(request, "entregas/lista.html", pedidos=pedidos)


@router.get("/{pedido_id}")
def detalhe_entrega(
    request: Request,
    banco: Sessao,
    pedido_id: int,
    usuario: Annotated[Usuario, Depends(exigir_usuario)],
) -> Response:
    pedido = banco.scalar(select(Pedido).where(Pedido.id == pedido_id))
    if pedido is None or pedido.entregador_id != usuario.id:
        raise ErroAplicacao("ERR-ENT-001")
    return renderizar(request, "entregas/detalhe.html", pedido=pedido)


@router.post("/{pedido_id}/confirmar")
def confirmar_entrega(
    request: Request,
    banco: Sessao,
    pedido_id: int,
    usuario: Annotated[Usuario, Depends(exigir_usuario)],
) -> Response:
    pedido = banco.scalar(select(Pedido).where(Pedido.id == pedido_id).with_for_update())
    if pedido is None or pedido.entregador_id != usuario.id:
        raise ErroAplicacao("ERR-ENT-001")
    if pedido.status != StatusPedido.SAIU_ENTREGA:
        raise ErroAplicacao("ERR-PED-002")
    pedido.status = StatusPedido.ENTREGUE
    registrar_historico(
        banco,
        pedido.id,
        StatusPedido.ENTREGUE,
        usuario.id,
        "Entrega confirmada pelo entregador.",
    )
    banco.commit()
    avisar(request, f"Entrega do pedido #{pedido.id} confirmada.")
    return redirecionar("/entregas")
