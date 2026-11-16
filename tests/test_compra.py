"""Checkout, pagamento simulado, pedidos e cancelamento."""

from __future__ import annotations

from decimal import Decimal

from fastapi.testclient import TestClient

from app.main import app
from tests.apoio import (
    adicionar_item,
    criar_pedido_pago,
    entrar,
    escalar,
    executar,
    finalizar_pedido,
    pagar,
    postar,
)
from tests.conftest import SENHA

CARTAO_RECUSA = "4242 4242 0000 0000"
CARTAO_INVALIDO = "1234 5678 9012 3456"


def test_checkout_exige_login(cliente_http: TestClient, dados: dict[str, int]) -> None:
    resposta = cliente_http.get("/checkout", follow_redirects=False)
    assert resposta.status_code == 303
    assert resposta.headers["location"].startswith("/login")


def test_fluxo_pix_aprova_e_baixa_estoque(cliente_http: TestClient, dados: dict[str, int]) -> None:
    entrar(cliente_http, "cliente@teste.local", SENHA)
    adicionar_item(cliente_http, dados["baunilha"], 2)
    pedido_id = finalizar_pedido(cliente_http)

    assert escalar("SELECT status FROM pedidos WHERE id=:id", id=pedido_id) == "recebido"
    assert escalar("SELECT frete FROM pedidos WHERE id=:id", id=pedido_id) == Decimal("8.00")
    assert escalar("SELECT valor FROM pagamentos WHERE pedido_id=:id", id=pedido_id) == Decimal(
        "28.00"
    )

    resposta = pagar(cliente_http, pedido_id)
    assert resposta.status_code == 303
    assert resposta.headers["location"] == f"/pedidos/{pedido_id}"
    assert escalar("SELECT status FROM pagamentos WHERE pedido_id=:id", id=pedido_id) == "aprovado"
    assert escalar("SELECT metodo FROM pagamentos WHERE pedido_id=:id", id=pedido_id) == "pix"
    assert escalar("SELECT estoque FROM produtos WHERE id=:id", id=dados["baunilha"]) == 3
    assert "aprovado" in cliente_http.get(f"/pedidos/{pedido_id}").text


def test_cartao_invalido_nao_baixa_estoque(cliente_http: TestClient, dados: dict[str, int]) -> None:
    entrar(cliente_http, "cliente@teste.local", SENHA)
    adicionar_item(cliente_http, dados["baunilha"], 2)
    pedido_id = finalizar_pedido(cliente_http)

    resposta = pagar(cliente_http, pedido_id, metodo="cartao", numero_cartao=CARTAO_INVALIDO)
    assert resposta.status_code == 422
    assert "ERR-PAG-002" in resposta.text
    assert escalar("SELECT status FROM pagamentos WHERE pedido_id=:id", id=pedido_id) == "pendente"
    assert escalar("SELECT estoque FROM produtos WHERE id=:id", id=dados["baunilha"]) == 5


def test_cartao_com_final_0000_e_recusado(cliente_http: TestClient, dados: dict[str, int]) -> None:
    entrar(cliente_http, "cliente@teste.local", SENHA)
    adicionar_item(cliente_http, dados["baunilha"], 2)
    pedido_id = finalizar_pedido(cliente_http)

    resposta = pagar(cliente_http, pedido_id, metodo="cartao", numero_cartao=CARTAO_RECUSA)
    assert resposta.status_code == 303
    pagina = cliente_http.get(f"/pedidos/{pedido_id}/pagamento").text
    assert "ERR-PAG-001" in pagina
    assert escalar("SELECT status FROM pagamentos WHERE pedido_id=:id", id=pedido_id) == "recusado"
    assert escalar("SELECT estoque FROM produtos WHERE id=:id", id=dados["baunilha"]) == 5


def test_estoque_insuficiente_no_pagamento(cliente_http: TestClient, dados: dict[str, int]) -> None:
    entrar(cliente_http, "cliente@teste.local", SENHA)
    adicionar_item(cliente_http, dados["chocolate"], 2)
    pedido_id = finalizar_pedido(cliente_http)
    executar("UPDATE produtos SET estoque = 0 WHERE id = :id", id=dados["chocolate"])

    resposta = pagar(cliente_http, pedido_id)
    assert resposta.status_code == 409
    assert "ERR-PAG-004" in resposta.text
    assert escalar("SELECT status FROM pedidos WHERE id=:id", id=pedido_id) == "recebido"
    assert escalar("SELECT status FROM pagamentos WHERE pedido_id=:id", id=pedido_id) == "pendente"
    assert escalar("SELECT estoque FROM produtos WHERE id=:id", id=dados["chocolate"]) == 0


def test_cancelamento_estorna_pagamento_e_estoque(
    cliente_http: TestClient, dados: dict[str, int]
) -> None:
    entrar(cliente_http, "cliente@teste.local", SENHA)
    pedido_id = criar_pedido_pago(cliente_http, dados["baunilha"])
    assert escalar("SELECT estoque FROM produtos WHERE id=:id", id=dados["baunilha"]) == 4

    resposta = postar(
        cliente_http,
        f"/pedidos/{pedido_id}/cancelar",
        {},
        pagina=f"/pedidos/{pedido_id}",
    )
    assert resposta.status_code == 303
    assert escalar("SELECT status FROM pedidos WHERE id=:id", id=pedido_id) == "cancelado"
    assert escalar("SELECT status FROM pagamentos WHERE pedido_id=:id", id=pedido_id) == "estornado"
    assert escalar("SELECT estoque FROM produtos WHERE id=:id", id=dados["baunilha"]) == 5


def test_pedido_de_outro_cliente_nao_e_acessivel(
    cliente_http: TestClient, dados: dict[str, int]
) -> None:
    entrar(cliente_http, "cliente@teste.local", SENHA)
    adicionar_item(cliente_http, dados["baunilha"])
    pedido_id = finalizar_pedido(cliente_http)

    with TestClient(app) as outro:
        entrar(outro, "outro@teste.local", SENHA)
        resposta = outro.get(
            f"/pedidos/{pedido_id}",
            headers={"accept": "application/problem+json"},
        )
    assert resposta.status_code == 404
    assert resposta.json()["codigo"] == "ERR-PED-001"
