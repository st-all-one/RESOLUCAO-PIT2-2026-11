"""Cadastro, login, logout e proteção CSRF."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app
from tests.apoio import entrar, escalar, executar, token_csrf
from tests.conftest import SENHA


def test_cadastro_autentica_e_grava_hash(cliente_http: TestClient, dados: dict[str, int]) -> None:
    token = token_csrf(cliente_http, "/cadastro")
    resposta = cliente_http.post(
        "/cadastro",
        data={
            "csrf_token": token,
            "nome": "Nova Cliente",
            "email": "nova@teste.local",
            "senha": SENHA,
            "confirmacao": SENHA,
        },
        follow_redirects=False,
    )
    assert resposta.status_code == 303
    assert resposta.headers["location"] == "/"
    papel = escalar("SELECT papel FROM usuarios WHERE email=:email", email="nova@teste.local")
    assert papel == "cliente"
    hash_gravado = escalar(
        "SELECT senha_hash FROM usuarios WHERE email=:email", email="nova@teste.local"
    )
    assert hash_gravado != SENHA
    assert cliente_http.get("/pedidos").status_code == 200


def test_cadastro_com_email_repetido(cliente_http: TestClient, dados: dict[str, int]) -> None:
    token = token_csrf(cliente_http, "/cadastro")
    resposta = cliente_http.post(
        "/cadastro",
        data={
            "csrf_token": token,
            "nome": "Duplicada",
            "email": "cliente@teste.local",
            "senha": SENHA,
            "confirmacao": SENHA,
        },
        follow_redirects=False,
    )
    assert resposta.status_code == 409
    assert "ERR-AUTH-002" in resposta.text


def test_login_com_senha_errada(cliente_http: TestClient, dados: dict[str, int]) -> None:
    token = token_csrf(cliente_http, "/login")
    resposta = cliente_http.post(
        "/login",
        data={
            "csrf_token": token,
            "email": "cliente@teste.local",
            "senha": "senha-errada",
            "next": "/",
        },
        follow_redirects=False,
    )
    assert resposta.status_code == 401
    assert "ERR-AUTH-001" in resposta.text


def test_login_de_conta_desativada(cliente_http: TestClient, dados: dict[str, int]) -> None:
    executar("UPDATE usuarios SET ativo = 0 WHERE id = :id", id=dados["cliente"])
    token = token_csrf(cliente_http, "/login")
    resposta = cliente_http.post(
        "/login",
        data={
            "csrf_token": token,
            "email": "cliente@teste.local",
            "senha": SENHA,
            "next": "/",
        },
        follow_redirects=False,
    )
    assert resposta.status_code == 403
    assert "ERR-AUTH-006" in resposta.text


def test_login_e_logout(cliente_http: TestClient, dados: dict[str, int]) -> None:
    entrar(cliente_http, "cliente@teste.local", SENHA, destino="/pedidos")
    assert cliente_http.get("/pedidos").status_code == 200

    token = token_csrf(cliente_http, "/")
    resposta = cliente_http.post(
        "/logout",
        data={"csrf_token": token},
        follow_redirects=False,
    )
    assert resposta.status_code == 303

    resposta = cliente_http.get("/pedidos", follow_redirects=False)
    assert resposta.status_code == 303
    assert "next=/pedidos" in resposta.headers["location"]


def test_mutacao_sem_csrf_e_rejeitada(cliente_http: TestClient, dados: dict[str, int]) -> None:
    resposta = cliente_http.post(
        "/login",
        data={"email": "cliente@teste.local", "senha": SENHA},
        follow_redirects=False,
    )
    assert resposta.status_code == 403
    assert "ERR-AUTH-008" in resposta.text


def test_token_de_outra_sessao_e_rejeitado(cliente_http: TestClient, dados: dict[str, int]) -> None:
    token = token_csrf(cliente_http, "/login")
    with TestClient(app) as outra_sessao:
        resposta = outra_sessao.post(
            "/login",
            data={
                "csrf_token": token,
                "email": "cliente@teste.local",
                "senha": SENHA,
                "next": "/",
            },
            follow_redirects=False,
        )
    assert resposta.status_code == 403
    assert "ERR-AUTH-008" in resposta.text
