"""Consulta de carrinho com validação contra o estado atual do catálogo."""

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import Produto
from app.services.carrinho import Carrinho


def carregar_itens(
    banco: Session,
    carrinho: Carrinho,
) -> tuple[list[tuple[Produto, int]], bool]:
    """Devolve itens válidos e se o carrinho precisou ser ajustado."""
    if not carrinho:
        return [], False
    produtos = {
        produto.id: produto
        for produto in banco.scalars(select(Produto).where(Produto.id.in_(carrinho))).all()
    }
    itens: list[tuple[Produto, int]] = []
    ajustado = False
    for produto_id in list(carrinho):
        produto = produtos.get(produto_id)
        if (
            produto is None
            or produto.excluido_em is not None
            or not produto.ativo
            or produto.categoria is None
            or not produto.categoria.ativo
        ):
            carrinho.pop(produto_id)
            ajustado = True
            continue
        if produto.estoque <= 0:
            carrinho.pop(produto_id)
            ajustado = True
            continue
        if carrinho[produto_id] > produto.estoque:
            carrinho[produto_id] = produto.estoque
            ajustado = True
        itens.append((produto, carrinho[produto_id]))
    return itens, ajustado
