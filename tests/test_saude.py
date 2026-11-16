"""Saúde da aplicação e Problem Details."""

from __future__ import annotations

from fastapi.testclient import TestClient


def test_health_responde_com_banco(cliente_http: TestClient) -> None:
    resposta = cliente_http.get("/health")
    assert resposta.status_code == 200
    assert resposta.json() == {"status": "ok", "db": "ok"}


def test_rota_inexistente_em_json(cliente_http: TestClient) -> None:
    resposta = cliente_http.get(
        "/nao-existe",
        headers={"accept": "application/problem+json"},
    )
    assert resposta.status_code == 404
    assert resposta.json()["codigo"] == "ERR-SYS-003"
