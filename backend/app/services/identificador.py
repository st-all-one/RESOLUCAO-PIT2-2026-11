"""Identificadores públicos de pedidos."""

from __future__ import annotations

import secrets
import time
from uuid import UUID


def uuid7() -> UUID:
    """Gera um UUIDv7 sem depender de `uuid.uuid7` (Python 3.13)."""
    timestamp = (time.time_ns() // 1_000_000) & ((1 << 48) - 1)
    aleatorio_a = secrets.randbits(12)
    aleatorio_b = secrets.randbits(62)
    valor = (timestamp << 80) | (0x7 << 76) | (aleatorio_a << 64) | (0b10 << 62) | aleatorio_b
    return UUID(int=valor)


def codigo_pedido() -> str:
    """Código curto e não sequencial exibido na URL do pedido."""
    return uuid7().hex[-8:]
