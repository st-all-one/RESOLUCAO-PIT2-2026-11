"""Conta do usuário: dados cadastrais, senha e endereços."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app
from tests.apoio import entrar, escalar, executar, postar, token_csrf
from tests.conftest import SENHA

ENDERECO = {
    "cep": "01310100",
    "logradouro": "Rua das Flores",
    "numero": "123",
    "complemento": "Apto 45",
    "bairro": "Jardim Paulista",
    "cidade": "São Paulo",
    "uf": "SP",
}


def test_conta_exige_login(cliente_http: TestClient, dados: dict[str, int]) -> None:
    resposta = cliente_http.get("/conta", follow_redirects=False)
    assert resposta.status_code == 303
    assert "/login" in resposta.headers["location"]


def test_atualiza_dados_cadastrais(cliente_http: TestClient, dados: dict[str, int]) -> None:
    entrar(cliente_http, "cliente@teste.local", SENHA)
    resposta = postar(
        cliente_http,
        "/conta/dados",
        {
            "nome": "Cliente Renomeado",
            "email": "renomeado@teste.local",
            "telefone": "11912345678",
        },
        pagina="/conta",
    )
    assert resposta.status_code == 303
    assert (
        escalar("SELECT nome FROM usuarios WHERE id=:id", id=dados["cliente"])
        == "Cliente Renomeado"
    )
    assert (
        escalar("SELECT email FROM usuarios WHERE id=:id", id=dados["cliente"])
        == "renomeado@teste.local"
    )
    pagina = cliente_http.get("/conta").text
    assert "Cliente Renomeado" in pagina
    assert "renomeado@teste.local" in pagina
    assert "11912345678" in pagina


def test_nao_aceita_email_de_outra_conta(cliente_http: TestClient, dados: dict[str, int]) -> None:
    entrar(cliente_http, "cliente@teste.local", SENHA)
    resposta = postar(
        cliente_http,
        "/conta/dados",
        {"nome": "Cliente Teste", "email": "outro@teste.local", "telefone": ""},
        pagina="/conta",
    )
    assert resposta.status_code == 409
    assert "ERR-AUTH-002" in resposta.text
    assert (
        escalar("SELECT email FROM usuarios WHERE id=:id", id=dados["cliente"])
        == "cliente@teste.local"
    )


def test_troca_de_senha_exige_senha_atual(cliente_http: TestClient, dados: dict[str, int]) -> None:
    entrar(cliente_http, "cliente@teste.local", SENHA)
    resposta = postar(
        cliente_http,
        "/conta/senha",
        {"senha_atual": "errada123", "nova": "NovaSenha@1", "confirmacao": "NovaSenha@1"},
        pagina="/conta",
    )
    assert resposta.status_code == 401
    assert "ERR-AUTH-001" in resposta.text

    resposta = postar(
        cliente_http,
        "/conta/senha",
        {"senha_atual": SENHA, "nova": "NovaSenha@1", "confirmacao": "NovaSenha@1"},
        pagina="/conta",
    )
    assert resposta.status_code == 303
    assert cliente_http.get("/conta").status_code == 200

    with TestClient(app) as nova_sessao:
        entrar(nova_sessao, "cliente@teste.local", "NovaSenha@1")
        assert nova_sessao.get("/conta").status_code == 200

    with TestClient(app) as senha_antiga:
        token = token_csrf(senha_antiga, "/login")
        resposta = senha_antiga.post(
            "/login",
            data={"csrf_token": token, "email": "cliente@teste.local", "senha": SENHA},
            follow_redirects=False,
        )
    assert resposta.status_code == 401


def test_gerencia_enderecos_e_endereco_principal(
    cliente_http: TestClient, dados: dict[str, int]
) -> None:
    entrar(cliente_http, "cliente@teste.local", SENHA)
    resposta = postar(cliente_http, "/conta/enderecos", ENDERECO, pagina="/conta")
    assert resposta.status_code == 303
    primeiro = escalar("SELECT id FROM enderecos WHERE usuario_id=:id", id=dados["cliente"])
    assert escalar("SELECT principal FROM enderecos WHERE id=:id", id=primeiro) == 1

    resposta = postar(
        cliente_http,
        "/conta/enderecos",
        {
            **ENDERECO,
            "numero": "999",
            "bairro": "Centro",
            "principal": "on",
        },
        pagina="/conta",
    )
    assert resposta.status_code == 303
    segundo = escalar(
        "SELECT id FROM enderecos WHERE usuario_id=:id AND numero=:numero",
        id=dados["cliente"],
        numero="999",
    )
    assert escalar("SELECT principal FROM enderecos WHERE id=:id", id=segundo) == 1
    assert escalar("SELECT principal FROM enderecos WHERE id=:id", id=primeiro) == 0

    resposta = postar(
        cliente_http,
        f"/conta/enderecos/{primeiro}/principal",
        {},
        pagina="/conta",
    )
    assert resposta.status_code == 303
    assert escalar("SELECT principal FROM enderecos WHERE id=:id", id=primeiro) == 1
    assert escalar("SELECT principal FROM enderecos WHERE id=:id", id=segundo) == 0

    resposta = postar(
        cliente_http,
        f"/conta/enderecos/{primeiro}/remover",
        {},
        pagina="/conta",
    )
    assert resposta.status_code == 303
    assert escalar("SELECT COUNT(*) FROM enderecos WHERE usuario_id=:id", id=dados["cliente"]) == 1
    assert escalar("SELECT principal FROM enderecos WHERE id=:id", id=segundo) == 1


def test_nao_gerencia_endereco_de_outra_conta(
    cliente_http: TestClient, dados: dict[str, int]
) -> None:
    executar(
        """
        INSERT INTO enderecos (usuario_id, cep, logradouro, numero, bairro, cidade, uf, principal)
        VALUES (:usuario_id, '01001000', 'Praça da Sé', '1', 'Sé', 'São Paulo', 'SP', 1)
        """,
        usuario_id=dados["outro"],
    )
    alheio = escalar("SELECT id FROM enderecos WHERE usuario_id=:id", id=dados["outro"])
    entrar(cliente_http, "cliente@teste.local", SENHA)
    resposta = postar(
        cliente_http,
        f"/conta/enderecos/{alheio}/remover",
        {},
        pagina="/conta",
    )
    assert resposta.status_code == 404
    assert "ERR-END-001" in resposta.text
    assert escalar("SELECT COUNT(*) FROM enderecos WHERE usuario_id=:id", id=dados["outro"]) == 1
