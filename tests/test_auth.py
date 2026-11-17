"""Cadastro, login, logout e proteção CSRF."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.controllers.comum import caminho_interno
from app.core.config import settings
from app.core.partida import validar_admin_inicial
from app.main import app
from app.services.seguranca import hash_senha
from tests.apoio import adicionar_item, entrar, escalar, executar, token_csrf
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


def test_login_de_conta_desconhecida_sugere_cadastro(
    cliente_http: TestClient, dados: dict[str, int]
) -> None:
    token = token_csrf(cliente_http, "/login")
    resposta = cliente_http.post(
        "/login",
        data={
            "csrf_token": token,
            "email": "naoexiste@teste.local",
            "senha": SENHA,
            "next": "/",
        },
        follow_redirects=False,
    )
    assert resposta.status_code == 401
    assert "Não encontramos uma conta com este e-mail." in resposta.text
    assert "/cadastro?email=naoexiste%40teste.local" in resposta.text
    assert "E-mail ou senha inválidos." not in resposta.text


def test_cadastro_preenche_email_vindo_do_login(cliente_http: TestClient) -> None:
    resposta = cliente_http.get("/cadastro?email=naoexiste%40teste.local")
    assert resposta.status_code == 200
    assert 'value="naoexiste@teste.local"' in resposta.text


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


def test_token_de_outra_sessao_nao_autentica(
    cliente_http: TestClient, dados: dict[str, int]
) -> None:
    token_a = token_csrf(cliente_http, "/login")
    with TestClient(app) as outra_sessao:
        token_b = token_csrf(outra_sessao, "/login")
        rejeitada = outra_sessao.post(
            "/login",
            data={
                "csrf_token": token_a,
                "email": "cliente@teste.local",
                "senha": SENHA,
                "next": "/",
            },
            follow_redirects=False,
        )
        aceita = outra_sessao.post(
            "/login",
            data={
                "csrf_token": token_b,
                "email": "cliente@teste.local",
                "senha": SENHA,
                "next": "/",
            },
            follow_redirects=False,
        )
    assert rejeitada.status_code == 403
    assert "ERR-AUTH-008" in rejeitada.text
    assert aceita.status_code == 303


def test_destino_externo_de_login_e_descartado() -> None:
    assert caminho_interno("/pedidos") == "/pedidos"
    assert caminho_interno("//evil.example") == "/"
    assert caminho_interno("/\\evil.example") == "/"
    assert caminho_interno("https://evil.example") == "/"
    assert caminho_interno("/%5Cevil.example") == "/"


def test_login_bloqueia_apos_cinco_falhas(cliente_http: TestClient, dados: dict[str, int]) -> None:
    token = token_csrf(cliente_http, "/login")
    for _ in range(5):
        resposta = cliente_http.post(
            "/login",
            data={
                "csrf_token": token,
                "email": "limite@teste.local",
                "senha": "senha-errada",
                "next": "/",
            },
            follow_redirects=False,
        )
        assert resposta.status_code == 401

    resposta = cliente_http.post(
        "/login",
        data={
            "csrf_token": token,
            "email": "limite@teste.local",
            "senha": "senha-errada",
            "next": "/",
        },
        follow_redirects=False,
    )
    assert resposta.status_code == 429
    assert "ERR-AUTH-010" in resposta.text


def test_logout_invalida_cookie_antigo(cliente_http: TestClient, dados: dict[str, int]) -> None:
    entrar(cliente_http, "cliente@teste.local", SENHA)
    cookie = cliente_http.cookies.get("cupcake_sessao")
    assert cookie is not None

    token = token_csrf(cliente_http, "/")
    assert (
        cliente_http.post(
            "/logout",
            data={"csrf_token": token},
            follow_redirects=False,
        ).status_code
        == 303
    )

    cliente_http.cookies.set("cupcake_sessao", cookie, domain="testserver", path="/")
    resposta = cliente_http.get("/pedidos", follow_redirects=False)
    assert resposta.status_code == 303
    assert "/login" in resposta.headers["location"]


def test_startup_recusa_senha_de_demonstracao(
    dados: dict[str, int], monkeypatch: pytest.MonkeyPatch
) -> None:
    executar(
        "UPDATE usuarios SET senha_hash=:hash WHERE id=:id",
        hash=hash_senha("Admin@123"),
        id=dados["admin"],
    )
    monkeypatch.setattr(settings, "app_env", "production")
    with pytest.raises(RuntimeError, match="demonstração"):
        validar_admin_inicial()


def test_login_preserva_carrinho_montado_como_visitante(
    cliente_http: TestClient, dados: dict[str, int]
) -> None:
    adicionar_item(cliente_http, dados["baunilha"], 2)
    entrar(cliente_http, "cliente@teste.local", SENHA, destino="/checkout")

    pagina = cliente_http.get("/carrinho").text
    assert "Cupcake Baunilha" in pagina
    assert 'value="2"' in pagina
    assert cliente_http.get("/checkout").status_code == 200


def test_cadastro_preserva_carrinho_montado_como_visitante(
    cliente_http: TestClient, dados: dict[str, int]
) -> None:
    adicionar_item(cliente_http, dados["baunilha"])
    token = token_csrf(cliente_http, "/cadastro")
    resposta = cliente_http.post(
        "/cadastro",
        data={
            "csrf_token": token,
            "nome": "Cliente com Carrinho",
            "email": "carrinho@teste.local",
            "senha": SENHA,
            "confirmacao": SENHA,
        },
        follow_redirects=False,
    )
    assert resposta.status_code == 303
    assert "Cupcake Baunilha" in cliente_http.get("/carrinho").text
