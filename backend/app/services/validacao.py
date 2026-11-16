"""Normalização e validação de campos de formulário."""

from __future__ import annotations

import re

CEP_RE = re.compile(r"^\d{8}$")
UF_RE = re.compile(r"^[A-Z]{2}$")


def normalizar_cep(valor: str) -> str | None:
    digitos = re.sub(r"\D", "", valor)
    return digitos if CEP_RE.fullmatch(digitos) else None


def normalizar_uf(valor: str) -> str | None:
    uf = valor.strip().upper()
    return uf if UF_RE.fullmatch(uf) else None


def normalizar_telefone(valor: str) -> str | None:
    digitos = re.sub(r"\D", "", valor)
    return digitos if 10 <= len(digitos) <= 11 else None


def texto(valor: str, *, minimo: int = 1, maximo: int = 255) -> str | None:
    limpo = valor.strip()
    if minimo <= len(limpo) <= maximo:
        return limpo
    return None
