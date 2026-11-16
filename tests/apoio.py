"""Ações e leituras reutilizadas pelos testes de integração."""

from __future__ import annotations

import re
from typing import cast

import httpx
from fastapi.testclient import TestClient
from sqlalchemy import text

from app.core.db import engine

PADRAO_TOKEN = re.compile(r'name="csrf_token" value="([^"]+)"')
PADRAO_PEDIDO = re.compile(r"/pedidos/([0-9a-f]{8})/pagamento")

ENDERECO = {
    "cep": "01310100",
    "logradouro": "Rua das Flores",
    "numero": "123",
    "complemento": "Apto 45",
    "bairro": "Jardim Paulista",
    "cidade": "São Paulo",
    "uf": "SP",
    "telefone": "11987654321",
}


def escalar(sql: str, **parametros: object) -> object:
    with engine.connect() as conexao:
        return conexao.execute(text(sql), parametros).scalar_one()


def executar(sql: str, **parametros: object) -> None:
    with engine.begin() as conexao:
        conexao.execute(text(sql), parametros)


def codigo_de(pedido_id: int) -> str:
    return cast(
        str,
        escalar("SELECT codigo FROM pedidos WHERE id=:id", id=pedido_id),
    )


def url_pedido(pedido_id: int, sufixo: str = "") -> str:
    return f"/pedidos/{codigo_de(pedido_id)}{sufixo}"


def token_csrf(cliente: TestClient, caminho: str = "/login") -> str:
    resposta = cliente.get(caminho)
    assert resposta.status_code == 200, (caminho, resposta.status_code, resposta.text[:200])
    achado = PADRAO_TOKEN.search(resposta.text)
    assert achado is not None, f"token CSRF ausente em {caminho}"
    return achado.group(1)


def entrar(cliente: TestClient, email: str, senha: str, destino: str = "/") -> None:
    token = token_csrf(cliente, "/login")
    resposta = cliente.post(
        "/login",
        data={"csrf_token": token, "email": email, "senha": senha, "next": destino},
        follow_redirects=False,
    )
    assert resposta.status_code == 303, (resposta.status_code, resposta.text[:300])


def postar(
    cliente: TestClient,
    caminho: str,
    dados: dict[str, str],
    *,
    pagina: str = "/",
) -> httpx.Response:
    token = token_csrf(cliente, pagina)
    return cast(
        httpx.Response,
        cliente.post(
            caminho,
            data={"csrf_token": token, **dados},
            follow_redirects=False,
        ),
    )


def adicionar_item(
    cliente: TestClient,
    produto_id: int,
    quantidade: int = 1,
    *,
    voltar: str = "/",
) -> httpx.Response:
    return postar(
        cliente,
        "/carrinho/adicionar",
        {
            "produto_id": str(produto_id),
            "quantidade": str(quantidade),
            "voltar": voltar,
        },
    )


def finalizar_pedido(cliente: TestClient, **alteracoes: str) -> int:
    corpo = {**ENDERECO, **alteracoes}
    resposta = postar(cliente, "/checkout", corpo, pagina="/checkout")
    assert resposta.status_code == 303, (resposta.status_code, resposta.text[:300])
    achado = PADRAO_PEDIDO.search(resposta.headers["location"])
    assert achado is not None, resposta.headers["location"]
    return int(
        cast(
            int,
            escalar("SELECT id FROM pedidos WHERE codigo=:codigo", codigo=achado.group(1)),
        )
    )


def pagar(
    cliente: TestClient,
    pedido_id: int,
    *,
    metodo: str = "pix",
    numero_cartao: str = "",
) -> httpx.Response:
    dados = {"metodo": metodo}
    if numero_cartao:
        dados["numero_cartao"] = numero_cartao
    caminho = url_pedido(pedido_id, "/pagamento")
    return postar(cliente, caminho, dados, pagina=caminho)


def criar_pedido_pago(cliente: TestClient, produto_id: int, quantidade: int = 1) -> int:
    resposta = adicionar_item(cliente, produto_id, quantidade)
    assert resposta.status_code == 303
    pedido_id = finalizar_pedido(cliente)
    resposta = pagar(cliente, pedido_id)
    assert resposta.status_code == 303, (resposta.status_code, resposta.text[:300])
    return pedido_id
