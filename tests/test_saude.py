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


def test_cabecalhos_de_seguranca(cliente_http: TestClient) -> None:
    resposta = cliente_http.get("/health")
    assert resposta.headers["x-content-type-options"] == "nosniff"
    assert resposta.headers["x-frame-options"] == "DENY"
    assert resposta.headers["referrer-policy"] == "same-origin"
    assert "frame-ancestors 'none'" in resposta.headers["content-security-policy"]
    assert "strict-transport-security" not in resposta.headers


def test_metodo_nao_permitido_preserva_allow(cliente_http: TestClient) -> None:
    resposta = cliente_http.get(
        "/logout",
        headers={"accept": "application/problem+json"},
    )
    assert resposta.status_code == 405
    assert resposta.json()["codigo"] == "ERR-SYS-004"
    assert resposta.headers["allow"] == "POST"


def test_json_sem_login_responde_401(cliente_http: TestClient) -> None:
    resposta = cliente_http.get(
        "/pedidos",
        headers={"accept": "application/problem+json"},
    )
    assert resposta.status_code == 401
    assert resposta.json()["codigo"] == "ERR-AUTH-009"
