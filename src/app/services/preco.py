"""Formatação e cálculos monetários puros."""

from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime
from decimal import Decimal

ZERO = Decimal("0.00")


def formatar_brl(valor: Decimal) -> str:
    texto = f"{valor:,.2f}"
    return "R$ " + texto.replace(",", "\x00").replace(".", ",").replace("\x00", ".")


def formatar_data(data: datetime) -> str:
    return data.strftime("%d/%m/%Y %H:%M")


def somar_itens(itens: Iterable[tuple[Decimal, int]]) -> Decimal:
    return sum((preco * quantidade for preco, quantidade in itens), start=ZERO)


def calcular_frete(
    subtotal: Decimal,
    *,
    valor: Decimal,
    gratis_acima: Decimal,
) -> Decimal:
    if subtotal <= ZERO:
        return ZERO
    if subtotal >= gratis_acima:
        return ZERO
    return valor


def quantidades_validas(quantidade: int) -> bool:
    return quantidade > 0
