"""Carrinho em sessão: funções puras sobre um mapa produto → quantidade."""

from __future__ import annotations

from collections.abc import MutableMapping
from typing import Any

from app.core.problemas import ErroAplicacao

Carrinho = dict[int, int]


def ler_carrinho(sessao: MutableMapping[str, Any]) -> Carrinho:
    bruto = sessao.get("carrinho")
    if not isinstance(bruto, dict):
        return {}
    resultado: Carrinho = {}
    for chave, valor in bruto.items():
        try:
            produto_id = int(chave)
            quantidade = int(valor)
        except (TypeError, ValueError):
            continue
        if produto_id > 0 and quantidade > 0:
            resultado[produto_id] = quantidade
    return resultado


def gravar_carrinho(sessao: MutableMapping[str, Any], carrinho: Carrinho) -> None:
    sessao["carrinho"] = {
        str(produto_id): quantidade
        for produto_id, quantidade in carrinho.items()
        if quantidade > 0
    }


def quantidade_total(carrinho: Carrinho) -> int:
    return sum(carrinho.values())


def adicionar(
    carrinho: Carrinho,
    produto_id: int,
    quantidade: int,
    estoque: int,
) -> Carrinho:
    if quantidade <= 0:
        raise ErroAplicacao("ERR-CAT-003")
    if estoque <= 0:
        raise ErroAplicacao("ERR-CAT-002")
    total = carrinho.get(produto_id, 0) + quantidade
    if total > estoque:
        raise ErroAplicacao(
            "ERR-CAR-002",
            campos={"quantidade": "Quantidade acima do estoque disponível."},
        )
    novo = dict(carrinho)
    novo[produto_id] = total
    return novo


def definir(
    carrinho: Carrinho,
    produto_id: int,
    quantidade: int,
    estoque: int,
) -> Carrinho:
    novo = dict(carrinho)
    if quantidade <= 0:
        novo.pop(produto_id, None)
        return novo
    if estoque <= 0:
        raise ErroAplicacao("ERR-CAT-002")
    if quantidade > estoque:
        raise ErroAplicacao(
            "ERR-CAR-002",
            campos={"quantidade": "Quantidade acima do estoque disponível."},
        )
    novo[produto_id] = quantidade
    return novo


def remover(carrinho: Carrinho, produto_id: int) -> Carrinho:
    novo = dict(carrinho)
    novo.pop(produto_id, None)
    return novo
