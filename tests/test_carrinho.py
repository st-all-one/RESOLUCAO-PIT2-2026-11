"""Carrinho: totais, frete, estoque e remoção."""

from __future__ import annotations

from fastapi.testclient import TestClient

from tests.apoio import adicionar_item, executar, postar


def test_totais_com_frete(cliente_http: TestClient, dados: dict[str, int]) -> None:
    assert adicionar_item(cliente_http, dados["baunilha"], 2).status_code == 303
    pagina = cliente_http.get("/carrinho").text
    assert "R$ 20,00" in pagina
    assert "R$ 8,00" in pagina
    assert "R$ 28,00" in pagina


def test_frete_gratis_acima_do_limite(cliente_http: TestClient, dados: dict[str, int]) -> None:
    assert adicionar_item(cliente_http, dados["festa"]).status_code == 303
    pagina = cliente_http.get("/carrinho").text
    assert "R$ 130,00" in pagina
    assert "R$ 0,00" in pagina


def test_quantidade_acima_do_estoque(cliente_http: TestClient, dados: dict[str, int]) -> None:
    resposta = adicionar_item(cliente_http, dados["baunilha"], 6)
    assert resposta.status_code == 303
    pagina = cliente_http.get("/carrinho").text
    assert "ERR-CAR-002" in pagina
    assert "carrinho está vazio" in pagina


def test_quantidade_invalida(cliente_http: TestClient, dados: dict[str, int]) -> None:
    resposta = adicionar_item(cliente_http, dados["baunilha"], 0)
    assert resposta.status_code == 303
    assert "ERR-CAT-003" in cliente_http.get("/carrinho").text


def test_atualizar_e_remover_item(cliente_http: TestClient, dados: dict[str, int]) -> None:
    adicionar_item(cliente_http, dados["baunilha"], 2)
    resposta = postar(
        cliente_http,
        "/carrinho/atualizar",
        {"produto_id": str(dados["baunilha"]), "quantidade": "1"},
    )
    assert resposta.status_code == 303
    pagina = cliente_http.get("/carrinho").text
    assert "R$ 10,00" in pagina
    assert "R$ 18,00" in pagina

    resposta = postar(
        cliente_http,
        "/carrinho/remover",
        {"produto_id": str(dados["baunilha"])},
    )
    assert resposta.status_code == 303
    assert "carrinho está vazio" in cliente_http.get("/carrinho").text


def test_ajuste_do_carrinho_aparece_na_propria_pagina(
    cliente_http: TestClient, dados: dict[str, int]
) -> None:
    adicionar_item(cliente_http, dados["baunilha"], 2)
    executar("UPDATE produtos SET estoque = 0 WHERE id = :id", id=dados["baunilha"])

    pagina = cliente_http.get("/carrinho").text
    assert "ERR-CAR-003" in pagina
    assert "carrinho está vazio" in pagina
    assert "ERR-CAR-003" not in cliente_http.get("/carrinho").text


def test_nao_adiciona_produto_inativo(cliente_http: TestClient, dados: dict[str, int]) -> None:
    resposta = adicionar_item(cliente_http, dados["inativo"])
    assert resposta.status_code == 404
    assert "ERR-CAT-001" in resposta.text
    assert "carrinho está vazio" in cliente_http.get("/carrinho").text
