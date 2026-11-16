"""Máquina de estados do pedido e rótulos de exibição."""

from __future__ import annotations

from typing import Final

from app.core.problemas import ErroAplicacao

ROTULOS_STATUS: Final[dict[str, str]] = {
    "recebido": "Recebido",
    "em_preparo": "Em preparo",
    "saiu_entrega": "Saiu para entrega",
    "entregue": "Entregue",
    "cancelado": "Cancelado",
}

TRANSICOES: Final[dict[str, frozenset[str]]] = {
    "recebido": frozenset({"em_preparo", "cancelado"}),
    "em_preparo": frozenset({"saiu_entrega", "cancelado"}),
    "saiu_entrega": frozenset({"entregue", "cancelado"}),
    "entregue": frozenset(),
    "cancelado": frozenset(),
}


def pode_transicionar(origem: str, destino: str) -> bool:
    return destino in TRANSICOES.get(origem, frozenset())


def validar_transicao(origem: str, destino: str) -> None:
    if not pode_transicionar(origem, destino):
        raise ErroAplicacao(
            "ERR-PED-002",
            campos={"status": f"Não é possível ir de {origem} para {destino}."},
        )


def transicoes_disponiveis(origem: str) -> frozenset[str]:
    return TRANSICOES.get(origem, frozenset())
