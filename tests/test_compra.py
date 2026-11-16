"""Checkout, pagamento simulado, pedidos e cancelamento."""

from __future__ import annotations

import re
from decimal import Decimal

import pytest
from fastapi.testclient import TestClient

from app.main import app
from tests.apoio import (
    ENDERECO,
    adicionar_item,
    codigo_de,
    criar_pedido_pago,
    entrar,
    escalar,
    executar,
    finalizar_pedido,
    pagar,
    postar,
    token_csrf,
    url_pedido,
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
    assert resposta.headers["location"] == f"/pedidos/{codigo_de(pedido_id)}"
    assert escalar("SELECT status FROM pagamentos WHERE pedido_id=:id", id=pedido_id) == "aprovado"
    assert escalar("SELECT metodo FROM pagamentos WHERE pedido_id=:id", id=pedido_id) == "pix"
    assert escalar("SELECT estoque FROM produtos WHERE id=:id", id=dados["baunilha"]) == 3
    assert "aprovado" in cliente_http.get(url_pedido(pedido_id)).text


def test_cartao_invalido_nao_baixa_estoque(cliente_http: TestClient, dados: dict[str, int]) -> None:
    entrar(cliente_http, "cliente@teste.local", SENHA)
    adicionar_item(cliente_http, dados["baunilha"], 2)
    pedido_id = finalizar_pedido(cliente_http)

    resposta = pagar(cliente_http, pedido_id, metodo="cartao", numero_cartao=CARTAO_INVALIDO)
    assert resposta.status_code == 422
    assert "ERR-PAG-002" in resposta.text
    assert 'value="cartao" checked' in resposta.text
    assert escalar("SELECT status FROM pagamentos WHERE pedido_id=:id", id=pedido_id) == "pendente"
    assert escalar("SELECT estoque FROM produtos WHERE id=:id", id=dados["baunilha"]) == 5


def test_cartao_com_final_0000_e_recusado(cliente_http: TestClient, dados: dict[str, int]) -> None:
    entrar(cliente_http, "cliente@teste.local", SENHA)
    adicionar_item(cliente_http, dados["baunilha"], 2)
    pedido_id = finalizar_pedido(cliente_http)

    resposta = pagar(cliente_http, pedido_id, metodo="cartao", numero_cartao=CARTAO_RECUSA)
    assert resposta.status_code == 303
    pagina = cliente_http.get(url_pedido(pedido_id, "/pagamento")).text
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
        url_pedido(pedido_id, "/cancelar"),
        {},
        pagina=url_pedido(pedido_id),
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
            url_pedido(pedido_id),
            headers={"accept": "application/problem+json"},
        )
    assert resposta.status_code == 404
    assert resposta.json()["codigo"] == "ERR-PED-001"


def test_nao_paga_pedido_cancelado(cliente_http: TestClient, dados: dict[str, int]) -> None:
    entrar(cliente_http, "cliente@teste.local", SENHA)
    adicionar_item(cliente_http, dados["baunilha"], 2)
    pedido_id = finalizar_pedido(cliente_http)
    token = token_csrf(cliente_http, url_pedido(pedido_id, "/pagamento"))
    postar(cliente_http, url_pedido(pedido_id, "/cancelar"), {}, pagina=url_pedido(pedido_id))

    resposta = cliente_http.post(
        url_pedido(pedido_id, "/pagamento"),
        data={"csrf_token": token, "metodo": "pix"},
        follow_redirects=False,
    )
    assert resposta.status_code == 409
    assert "ERR-PED-003" in resposta.text
    assert escalar("SELECT status FROM pagamentos WHERE pedido_id=:id", id=pedido_id) == "cancelado"
    assert escalar("SELECT estoque FROM produtos WHERE id=:id", id=dados["baunilha"]) == 5


def test_nao_repaga_pedido_estornado(cliente_http: TestClient, dados: dict[str, int]) -> None:
    entrar(cliente_http, "cliente@teste.local", SENHA)
    pedido_id = criar_pedido_pago(cliente_http, dados["baunilha"])
    token = token_csrf(cliente_http, url_pedido(pedido_id))
    postar(cliente_http, url_pedido(pedido_id, "/cancelar"), {}, pagina=url_pedido(pedido_id))

    resposta = cliente_http.post(
        url_pedido(pedido_id, "/pagamento"),
        data={"csrf_token": token, "metodo": "pix"},
        follow_redirects=False,
    )
    assert resposta.status_code == 409
    assert "ERR-PED-003" in resposta.text
    assert escalar("SELECT status FROM pagamentos WHERE pedido_id=:id", id=pedido_id) == "estornado"
    assert escalar("SELECT estoque FROM produtos WHERE id=:id", id=dados["baunilha"]) == 5


def test_pagamento_duplicado_nao_baixa_estoque(
    cliente_http: TestClient, dados: dict[str, int]
) -> None:
    entrar(cliente_http, "cliente@teste.local", SENHA)
    pedido_id = criar_pedido_pago(cliente_http, dados["baunilha"])
    token = token_csrf(cliente_http, url_pedido(pedido_id))

    resposta = cliente_http.post(
        url_pedido(pedido_id, "/pagamento"),
        data={"csrf_token": token, "metodo": "pix"},
        follow_redirects=False,
    )
    assert resposta.status_code == 409
    assert "ERR-PAG-003" in resposta.text
    assert escalar("SELECT estoque FROM produtos WHERE id=:id", id=dados["baunilha"]) == 4


def test_falha_parcial_de_estoque_nao_baixa_nenhum_item(
    cliente_http: TestClient, dados: dict[str, int]
) -> None:
    entrar(cliente_http, "cliente@teste.local", SENHA)
    adicionar_item(cliente_http, dados["chocolate"], 2)
    adicionar_item(cliente_http, dados["baunilha"], 1)
    pedido_id = finalizar_pedido(cliente_http)
    executar("UPDATE produtos SET estoque = 0 WHERE id = :id", id=dados["chocolate"])

    resposta = pagar(cliente_http, pedido_id)
    assert resposta.status_code == 409
    assert "ERR-PAG-004" in resposta.text
    assert escalar("SELECT estoque FROM produtos WHERE id=:id", id=dados["chocolate"]) == 0
    assert escalar("SELECT estoque FROM produtos WHERE id=:id", id=dados["baunilha"]) == 5
    assert escalar("SELECT status FROM pagamentos WHERE pedido_id=:id", id=pedido_id) == "pendente"


def test_outro_cliente_nao_paga_nem_cancela(
    cliente_http: TestClient, dados: dict[str, int]
) -> None:
    entrar(cliente_http, "cliente@teste.local", SENHA)
    adicionar_item(cliente_http, dados["baunilha"], 2)
    pedido_id = finalizar_pedido(cliente_http)

    with TestClient(app) as outro:
        entrar(outro, "outro@teste.local", SENHA)
        token = token_csrf(outro, "/")
        pagamento = outro.post(
            url_pedido(pedido_id, "/pagamento"),
            data={"csrf_token": token, "metodo": "pix"},
            follow_redirects=False,
            headers={"accept": "application/problem+json"},
        )
        cancelamento = outro.post(
            url_pedido(pedido_id, "/cancelar"),
            data={"csrf_token": token},
            follow_redirects=False,
            headers={"accept": "application/problem+json"},
        )

    assert pagamento.status_code == 404
    assert pagamento.json()["codigo"] == "ERR-PED-001"
    assert cancelamento.status_code == 404
    assert cancelamento.json()["codigo"] == "ERR-PED-001"
    assert escalar("SELECT status FROM pedidos WHERE id=:id", id=pedido_id) == "recebido"
    assert escalar("SELECT status FROM pagamentos WHERE pedido_id=:id", id=pedido_id) == "pendente"
    assert escalar("SELECT estoque FROM produtos WHERE id=:id", id=dados["baunilha"]) == 5


def test_checkout_persiste_telefone_do_perfil(
    cliente_http: TestClient, dados: dict[str, int]
) -> None:
    entrar(cliente_http, "cliente@teste.local", SENHA)
    adicionar_item(cliente_http, dados["baunilha"])
    finalizar_pedido(cliente_http, telefone="11912345678")

    assert (
        escalar("SELECT telefone FROM usuarios WHERE id=:id", id=dados["cliente"]) == "11912345678"
    )


def test_checkout_ajusta_carrinho_antes_de_criar_pedido(
    cliente_http: TestClient, dados: dict[str, int]
) -> None:
    entrar(cliente_http, "cliente@teste.local", SENHA)
    adicionar_item(cliente_http, dados["baunilha"], 2)
    token = token_csrf(cliente_http, "/")
    executar("UPDATE produtos SET estoque = 1 WHERE id = :id", id=dados["baunilha"])

    resposta = cliente_http.post(
        "/checkout",
        data={"csrf_token": token, **ENDERECO},
        follow_redirects=False,
    )
    assert resposta.status_code == 409
    assert "ERR-CAR-002" in resposta.text
    assert escalar("SELECT COUNT(*) FROM pedidos") == 0
    assert escalar("SELECT COUNT(*) FROM pagamentos") == 0
    pagina = cliente_http.get("/carrinho").text
    assert 'value="1"' in pagina


def test_consulta_cep_devolve_endereco(
    cliente_http: TestClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr(
        "app.controllers.checkout._consultar_cep",
        lambda _cep: {
            "logradouro": "Rua das Flores",
            "bairro": "Jardim Paulista",
            "cidade": "São Paulo",
            "uf": "SP",
        },
    )
    resposta = cliente_http.get("/cep/01310100")
    assert resposta.status_code == 200
    assert resposta.json()["cidade"] == "São Paulo"
    assert resposta.json()["uf"] == "SP"


def test_consulta_cep_rejeita_cep_invalido(cliente_http: TestClient) -> None:
    resposta = cliente_http.get(
        "/cep/123",
        headers={"accept": "application/problem+json"},
    )
    assert resposta.status_code == 422
    assert resposta.json()["codigo"] == "ERR-CHK-002"


def test_checkout_permite_ajustar_item_sem_sair_da_tela(
    cliente_http: TestClient, dados: dict[str, int]
) -> None:
    entrar(cliente_http, "cliente@teste.local", SENHA)
    adicionar_item(cliente_http, dados["baunilha"], 1)
    token = token_csrf(cliente_http, "/checkout")

    resposta = cliente_http.post(
        "/checkout",
        data={"csrf_token": token, **ENDERECO, "item": f"mais:{dados['baunilha']}"},
        follow_redirects=False,
    )
    assert resposta.status_code == 200
    assert re.search(
        rf'data-quantidade="{dados["baunilha"]}">\s*2\s*<',
        resposta.text,
    )
    assert 'value="Rua das Flores"' in resposta.text
    assert 'value="01310100"' in resposta.text
    assert escalar("SELECT COUNT(*) FROM pedidos") == 0

    token = token_csrf(cliente_http, "/checkout")
    resposta = cliente_http.post(
        "/checkout",
        data={"csrf_token": token, **ENDERECO, "item": f"remover:{dados['baunilha']}"},
        follow_redirects=False,
    )
    assert resposta.status_code == 303
    assert resposta.headers["location"] == "/carrinho"


def test_pedido_exibe_codigo_publico_na_url(
    cliente_http: TestClient, dados: dict[str, int]
) -> None:
    entrar(cliente_http, "cliente@teste.local", SENHA)
    adicionar_item(cliente_http, dados["baunilha"])
    pedido_id = finalizar_pedido(cliente_http)
    codigo = codigo_de(pedido_id)

    assert re.fullmatch(r"[0-9a-f]{8}", codigo)
    pagina = cliente_http.get(f"/pedidos/{codigo}")
    assert pagina.status_code == 200
    assert "Pedido #" in pagina.text
    assert f"/pedidos/{pedido_id}" not in pagina.text


@pytest.mark.parametrize(
    ("alteracao", "codigo"),
    [
        ({"cep": "123"}, "ERR-CHK-002"),
        ({"uf": "S1"}, "ERR-CHK-003"),
        ({"telefone": "123"}, "ERR-CHK-001"),
    ],
)
def test_checkout_rejeita_endereco_invalido(
    cliente_http: TestClient,
    dados: dict[str, int],
    alteracao: dict[str, str],
    codigo: str,
) -> None:
    entrar(cliente_http, "cliente@teste.local", SENHA)
    adicionar_item(cliente_http, dados["baunilha"])
    token = token_csrf(cliente_http, "/")

    resposta = cliente_http.post(
        "/checkout",
        data={"csrf_token": token, **ENDERECO, **alteracao},
        follow_redirects=False,
    )
    assert resposta.status_code == 422
    assert codigo in resposta.text
    assert escalar("SELECT COUNT(*) FROM pedidos") == 0
    assert escalar("SELECT COUNT(*) FROM pagamentos") == 0
