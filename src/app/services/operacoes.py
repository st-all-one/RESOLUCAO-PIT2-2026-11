"""Operações de pedido que alteram estoque e histórico em conjunto."""

from __future__ import annotations

from sqlalchemy import update
from sqlalchemy.orm import Session

from app.models import HistoricoPedido, Pedido, Produto


def registrar_historico(
    banco: Session,
    pedido_id: int,
    status: str,
    usuario_id: int | None,
    observacao: str | None = None,
) -> None:
    banco.add(
        HistoricoPedido(
            pedido_id=pedido_id,
            status=status,
            usuario_id=usuario_id,
            observacao=observacao,
        )
    )


def restaurar_estoque(banco: Session, pedido: Pedido) -> None:
    for item in pedido.itens:
        banco.execute(
            update(Produto)
            .where(Produto.id == item.produto_id)
            .values(estoque=Produto.estoque + item.quantidade)
            .execution_options(synchronize_session=False)
        )


def cancelar_pedido(
    banco: Session,
    pedido: Pedido,
    usuario_id: int | None,
    observacao: str,
) -> None:
    """Cancela, repõe estoque quando pago e ajusta o pagamento."""
    pagamento = pedido.pagamento
    if pagamento is not None and pagamento.status == "aprovado":
        restaurar_estoque(banco, pedido)
        pagamento.status = "estornado"
    elif pagamento is not None and pagamento.status == "pendente":
        pagamento.status = "cancelado"
    pedido.status = "cancelado"
    registrar_historico(banco, pedido.id, "cancelado", usuario_id, observacao)
