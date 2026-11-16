"""Gateway de pagamento simulado: Luhn, PIX e cartão de teste."""

from __future__ import annotations

import re
import secrets
from dataclasses import dataclass

from app.core.problemas import ErroAplicacao

METODOS = frozenset({"pix", "cartao"})


@dataclass(frozen=True, slots=True)
class ResultadoPagamento:
    aprovado: bool
    codigo: str
    ultimos4: str | None


def somente_digitos(texto: str) -> str:
    return re.sub(r"\D", "", texto)


def validar_luhn(numero: str) -> bool:
    digitos = somente_digitos(numero)
    if not 13 <= len(digitos) <= 19:
        return False
    soma = 0
    dobrar = False
    for caractere in reversed(digitos):
        digito = int(caractere)
        if dobrar:
            digito *= 2
            if digito > 9:
                digito -= 9
        soma += digito
        dobrar = not dobrar
    return soma % 10 == 0


def simular(metodo: str, numero_cartao: str | None = None) -> ResultadoPagamento:
    if metodo == "pix":
        return ResultadoPagamento(
            aprovado=True,
            codigo=f"PIX-{secrets.token_hex(4).upper()}",
            ultimos4=None,
        )
    if metodo == "cartao":
        digitos = somente_digitos(numero_cartao or "")
        if not validar_luhn(digitos):
            raise ErroAplicacao(
                "ERR-PAG-002",
                campos={"numero_cartao": "Número de cartão inválido."},
            )
        ultimos4 = digitos[-4:]
        if ultimos4 == "0000":
            return ResultadoPagamento(aprovado=False, codigo="", ultimos4=ultimos4)
        return ResultadoPagamento(
            aprovado=True,
            codigo=f"AUT-{secrets.token_hex(4).upper()}",
            ultimos4=ultimos4,
        )
    raise ErroAplicacao(
        "ERR-VAL-001",
        campos={"metodo": "Método de pagamento inválido."},
    )
