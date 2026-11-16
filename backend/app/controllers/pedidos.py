"""Meus pedidos: lista, detalhe e cancelamento pelo cliente."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Request
from fastapi.responses import Response
from sqlalchemy import select

from app.controllers.comum import Sessao, avisar, redirecionar, renderizar
from app.core.acesso import exigir_usuario
from app.core.csrf import validar_csrf
from app.core.problemas import ErroAplicacao
from app.models import Pedido, StatusPedido, Usuario
from app.services.operacoes import cancelar_pedido

router = APIRouter(dependencies=[Depends(validar_csrf)])


@router.get("/pedidos")
def lista_pedidos(
    request: Request,
    banco: Sessao,
    usuario: Annotated[Usuario, Depends(exigir_usuario)],
) -> Response:
    pedidos = list(
        banco.scalars(
            select(Pedido).where(Pedido.cliente_id == usuario.id).order_by(Pedido.criado_em.desc())
        ).all()
    )
    return renderizar(request, "pedidos/lista.html", pedidos=pedidos)


@router.get("/pedidos/{codigo}")
def detalhe_pedido(
    request: Request,
    banco: Sessao,
    codigo: str,
    usuario: Annotated[Usuario, Depends(exigir_usuario)],
) -> Response:
    pedido = banco.scalar(select(Pedido).where(Pedido.codigo == codigo))
    if pedido is None or pedido.cliente_id != usuario.id:
        raise ErroAplicacao("ERR-PED-001")
    return renderizar(request, "pedidos/detalhe.html", pedido=pedido)


@router.post("/pedidos/{codigo}/cancelar")
def cancelar(
    request: Request,
    banco: Sessao,
    codigo: str,
    usuario: Annotated[Usuario, Depends(exigir_usuario)],
) -> Response:
    pedido = banco.scalar(select(Pedido).where(Pedido.codigo == codigo).with_for_update())
    if pedido is None or pedido.cliente_id != usuario.id:
        raise ErroAplicacao("ERR-PED-001")
    if pedido.status != StatusPedido.RECEBIDO:
        raise ErroAplicacao("ERR-PED-003")
    cancelar_pedido(banco, pedido, usuario.id, "Cancelado pelo cliente.")
    banco.commit()
    avisar(request, "Pedido cancelado.", tipo="info")
    return redirecionar(f"/pedidos/{pedido.codigo}")
