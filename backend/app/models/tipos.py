"""Enumerações de domínio (papéis, status e métodos)."""

from __future__ import annotations

from enum import StrEnum


class Papel(StrEnum):
    CLIENTE = "cliente"
    ENTREGADOR = "entregador"
    ADMIN = "admin"


class StatusPedido(StrEnum):
    RECEBIDO = "recebido"
    EM_PREPARO = "em_preparo"
    SAIU_ENTREGA = "saiu_entrega"
    ENTREGUE = "entregue"
    CANCELADO = "cancelado"


class StatusPagamento(StrEnum):
    PENDENTE = "pendente"
    APROVADO = "aprovado"
    RECUSADO = "recusado"
    ESTORNADO = "estornado"
    CANCELADO = "cancelado"


class MetodoPagamento(StrEnum):
    PIX = "pix"
    CARTAO = "cartao"
