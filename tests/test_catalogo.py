"""Vitrine, busca, filtro e detalhe de produto."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_vitrine_lista_apenas_produtos_ativos(
    cliente_http: TestClient, dados: dict[str, int]
) -> None:
    pagina = cliente_http.get("/").text
    assert "Cupcake Baunilha" in pagina
    assert "Cupcake Festa" in pagina
    assert "Cupcake Inativo" not in pagina


def test_busca_textual_filtra(cliente_http: TestClient, dados: dict[str, int]) -> None:
    pagina = cliente_http.get("/?q=chocolate").text
    assert "Cupcake Chocolate" in pagina
    assert "Cupcake Baunilha" not in pagina


def test_filtro_por_categoria(cliente_http: TestClient, dados: dict[str, int]) -> None:
    pagina = cliente_http.get("/?categoria=veganos").text
    assert "Cupcake Vegano" in pagina
    assert "Cupcake Chocolate" not in pagina


def test_detalhe_por_slug(cliente_http: TestClient, dados: dict[str, int]) -> None:
    resposta = cliente_http.get("/produtos/cupcake-baunilha")
    assert resposta.status_code == 200
    assert "Cupcake Baunilha" in resposta.text


def test_detalhe_inexistente_em_json(cliente_http: TestClient, dados: dict[str, int]) -> None:
    resposta = cliente_http.get(
        "/produtos/nao-existe",
        headers={"accept": "application/problem+json"},
    )
    assert resposta.status_code == 404
    assert resposta.json()["codigo"] == "ERR-CAT-001"
