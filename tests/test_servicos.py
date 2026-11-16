"""Funções puras: dinheiro, carrinho, pagamento, slug, validação e senha."""

from __future__ import annotations

from decimal import Decimal

import pytest

from app.core.problemas import ErroAplicacao
from app.services.carrinho import adicionar, definir, quantidade_total, remover
from app.services.pagamento import simular, validar_luhn
from app.services.pedido import pode_transicionar, validar_transicao
from app.services.preco import calcular_frete, formatar_brl, somar_itens
from app.services.seguranca import hash_senha, senha_forte, verificar_senha
from app.services.slug import gerar_slug
from app.services.validacao import normalizar_cep, normalizar_telefone, normalizar_uf, texto


def test_formata_e_soma_valores() -> None:
    assert formatar_brl(Decimal("1234.56")) == "R$ 1.234,56"
    assert somar_itens([(Decimal("10.00"), 2), (Decimal("5.50"), 1)]) == Decimal("25.50")


def test_frete_com_limites() -> None:
    assert calcular_frete(Decimal("0"), valor=Decimal("8.00"), gratis_acima=Decimal("120")) == 0
    assert calcular_frete(
        Decimal("100"), valor=Decimal("8.00"), gratis_acima=Decimal("120")
    ) == Decimal("8.00")
    assert calcular_frete(Decimal("120"), valor=Decimal("8.00"), gratis_acima=Decimal("120")) == 0


def test_luhn_e_simulacao_de_pagamento() -> None:
    assert validar_luhn("4242 4242 4242 4242") is True
    assert validar_luhn("1234 5678 9012 3456") is False
    assert validar_luhn("123") is False

    pix = simular("pix")
    assert pix.aprovado is True
    assert pix.codigo.startswith("PIX-")

    aprovado = simular("cartao", "4242 4242 4242 4242")
    assert aprovado.aprovado is True
    assert aprovado.ultimos4 == "4242"

    recusado = simular("cartao", "4242 4242 0000 0000")
    assert recusado.aprovado is False

    with pytest.raises(ErroAplicacao) as excinfo:
        simular("cartao", "1234 5678 9012 3456")
    assert excinfo.value.codigo == "ERR-PAG-002"

    with pytest.raises(ErroAplicacao) as excinfo:
        simular("boleto")
    assert excinfo.value.codigo == "ERR-VAL-001"


def test_slug_remove_acentos_e_pontuacao() -> None:
    assert gerar_slug("Cupcake de Chocolate!") == "cupcake-de-chocolate"
    assert gerar_slug("Açaí com Banana") == "acai-com-banana"
    assert gerar_slug("!!!") == "item"


def test_validacao_de_campos() -> None:
    assert normalizar_cep("01310-100") == "01310100"
    assert normalizar_cep("123") is None
    assert normalizar_uf("sp") == "SP"
    assert normalizar_uf("S1") is None
    assert normalizar_telefone("(11) 98765-4321") == "11987654321"
    assert normalizar_telefone("123") is None
    assert texto("  Cupcake  ") == "Cupcake"
    assert texto("x", minimo=2) is None


def test_senha_com_hash_e_politica() -> None:
    hash_ = hash_senha("Senha@123")
    assert hash_ != "Senha@123"
    assert verificar_senha("Senha@123", hash_) is True
    assert verificar_senha("outra", hash_) is False
    assert senha_forte("Senha@123") is True
    assert senha_forte("12345678") is False


def test_transicoes_da_maquina_de_estados() -> None:
    assert pode_transicionar("recebido", "em_preparo") is True
    assert pode_transicionar("entregue", "recebido") is False
    with pytest.raises(ErroAplicacao) as excinfo:
        validar_transicao("entregue", "recebido")
    assert excinfo.value.codigo == "ERR-PED-002"


def test_carrinho_puro_respeita_estoque() -> None:
    assert adicionar({}, 1, 2, estoque=5) == {1: 2}
    assert adicionar({1: 2}, 1, 3, estoque=5) == {1: 5}
    with pytest.raises(ErroAplicacao) as excinfo:
        adicionar({}, 1, 6, estoque=5)
    assert excinfo.value.codigo == "ERR-CAR-002"

    with pytest.raises(ErroAplicacao) as excinfo:
        definir({}, 1, 1, estoque=0)
    assert excinfo.value.codigo == "ERR-CAT-002"

    assert definir({1: 2}, 1, 0, estoque=5) == {}
    assert remover({1: 2}, 1) == {}
    assert quantidade_total({1: 2, 2: 3}) == 5
