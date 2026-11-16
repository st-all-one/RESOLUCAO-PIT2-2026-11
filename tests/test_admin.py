"""Administração: autorização, CRUD, transições e relatório."""

from __future__ import annotations

from decimal import Decimal

from fastapi.testclient import TestClient

from app.main import app
from tests.apoio import (
    adicionar_item,
    criar_pedido_pago,
    entrar,
    escalar,
    finalizar_pedido,
    pagar,
    postar,
)
from tests.conftest import SENHA

NOVO_PRODUTO = {
    "nome": "Cupcake Novo",
    "descricao": "Criado pela suíte de testes.",
    "alergenicos": "Leite e glúten.",
    "preco": "15,90",
    "estoque": "4",
    "ativo": "on",
}


def test_cliente_nao_acessa_administracao(cliente_http: TestClient, dados: dict[str, int]) -> None:
    entrar(cliente_http, "cliente@teste.local", SENHA)
    resposta = cliente_http.get(
        "/admin/produtos",
        headers={"accept": "application/problem+json"},
    )
    assert resposta.status_code == 403
    assert resposta.json()["codigo"] == "ERR-AUTH-007"


def test_admin_cria_categoria_e_produto_ativo(
    cliente_http: TestClient, dados: dict[str, int]
) -> None:
    entrar(cliente_http, "admin@teste.local", SENHA)
    resposta = postar(
        cliente_http,
        "/admin/categorias",
        {"nome": "Sazonais"},
        pagina="/admin/categorias",
    )
    assert resposta.status_code == 303
    categoria_id = escalar("SELECT id FROM categorias WHERE nome=:nome", nome="Sazonais")
    assert categoria_id is not None

    resposta = postar(
        cliente_http,
        "/admin/produtos/novo",
        {**NOVO_PRODUTO, "categoria_id": str(categoria_id)},
        pagina="/admin/produtos/novo",
    )
    assert resposta.status_code == 303
    assert escalar("SELECT ativo FROM produtos WHERE slug=:slug", slug="cupcake-novo") == 1
    assert escalar("SELECT preco FROM produtos WHERE slug=:slug", slug="cupcake-novo") == Decimal(
        "15.90"
    )


def test_admin_rejeita_preco_invalido_e_nome_duplicado(
    cliente_http: TestClient, dados: dict[str, int]
) -> None:
    entrar(cliente_http, "admin@teste.local", SENHA)
    resposta = postar(
        cliente_http,
        "/admin/produtos/novo",
        {
            **NOVO_PRODUTO,
            "categoria_id": str(dados["tradicionais"]),
            "preco": "0",
        },
        pagina="/admin/produtos/novo",
    )
    assert resposta.status_code == 422
    assert "ERR-ADM-003" in resposta.text

    resposta = postar(
        cliente_http,
        "/admin/produtos/novo",
        {
            **NOVO_PRODUTO,
            "categoria_id": str(dados["tradicionais"]),
            "nome": "Cupcake Baunilha",
        },
        pagina="/admin/produtos/novo",
    )
    assert resposta.status_code == 409
    assert "ERR-ADM-008" in resposta.text


def test_transicoes_exigem_pagamento_e_entregador(
    cliente_http: TestClient, dados: dict[str, int]
) -> None:
    entrar(cliente_http, "cliente@teste.local", SENHA)
    adicionar_item(cliente_http, dados["baunilha"])
    pedido_id = finalizar_pedido(cliente_http)

    with TestClient(app) as admin:
        entrar(admin, "admin@teste.local", SENHA)
        pagina = f"/admin/pedidos/{pedido_id}"

        resposta = postar(admin, f"{pagina}/status", {"destino": "em_preparo"}, pagina=pagina)
        assert resposta.status_code == 409
        assert "ERR-PED-002" in resposta.text

        assert pagar(cliente_http, pedido_id).status_code == 303

        resposta = postar(admin, f"{pagina}/status", {"destino": "em_preparo"}, pagina=pagina)
        assert resposta.status_code == 303

        resposta = postar(admin, f"{pagina}/status", {"destino": "saiu_entrega"}, pagina=pagina)
        assert resposta.status_code == 409
        assert "ERR-PED-002" in resposta.text

        resposta = postar(
            admin,
            f"{pagina}/status",
            {"destino": "saiu_entrega", "entregador_id": str(dados["entregador"])},
            pagina=pagina,
        )
        assert resposta.status_code == 303

    assert (
        escalar("SELECT entregador_id FROM pedidos WHERE id=:id", id=pedido_id)
        == dados["entregador"]
    )


def test_relatorio_soma_pedidos_pagos(cliente_http: TestClient, dados: dict[str, int]) -> None:
    entrar(cliente_http, "cliente@teste.local", SENHA)
    adicionar_item(cliente_http, dados["baunilha"], 2)
    pedido_id = finalizar_pedido(cliente_http)
    assert pagar(cliente_http, pedido_id).status_code == 303

    with TestClient(app) as admin:
        entrar(admin, "admin@teste.local", SENHA)
        pagina = admin.get("/admin/relatorio").text
    assert "R$ 28,00" in pagina
    assert "Cupcake Baunilha" in pagina


def test_admin_nao_altera_a_propria_conta(cliente_http: TestClient, dados: dict[str, int]) -> None:
    entrar(cliente_http, "admin@teste.local", SENHA)
    resposta = postar(
        cliente_http,
        f"/admin/usuarios/{dados['admin']}/papel",
        {"papel": "cliente"},
    )
    assert resposta.status_code == 409
    assert "ERR-ADM-005" in resposta.text

    resposta = postar(
        cliente_http,
        f"/admin/usuarios/{dados['admin']}/ativo",
        {},
    )
    assert resposta.status_code == 409
    assert "ERR-ADM-005" in resposta.text


def test_categoria_inexistente_responde_404(
    cliente_http: TestClient, dados: dict[str, int]
) -> None:
    entrar(cliente_http, "admin@teste.local", SENHA)
    resposta = postar(
        cliente_http,
        "/admin/categorias/999999/editar",
        {"nome": "Nova"},
        pagina="/admin/categorias",
    )
    assert resposta.status_code == 404
    assert "ERR-ADM-009" in resposta.text


def test_nao_exclui_produto_com_historico(cliente_http: TestClient, dados: dict[str, int]) -> None:
    with TestClient(app) as cliente:
        entrar(cliente, "cliente@teste.local", SENHA)
        criar_pedido_pago(cliente, dados["baunilha"])

    entrar(cliente_http, "admin@teste.local", SENHA)
    resposta = postar(
        cliente_http,
        f"/admin/produtos/{dados['baunilha']}/excluir",
        {},
        pagina="/admin/produtos",
    )
    assert resposta.status_code == 303
    assert escalar("SELECT COUNT(*) FROM produtos WHERE id=:id", id=dados["baunilha"]) == 1
    assert "ERR-ADM-007" in cliente_http.get("/admin/produtos").text


def test_nao_exclui_categoria_com_produtos(cliente_http: TestClient, dados: dict[str, int]) -> None:
    entrar(cliente_http, "admin@teste.local", SENHA)
    resposta = postar(
        cliente_http,
        f"/admin/categorias/{dados['tradicionais']}/excluir",
        {},
        pagina="/admin/categorias",
    )
    assert resposta.status_code == 303
    assert escalar("SELECT COUNT(*) FROM categorias WHERE id=:id", id=dados["tradicionais"]) == 1
    assert "ERR-ADM-002" in cliente_http.get("/admin/categorias").text


def test_relatorio_ignora_pedido_nao_pago(cliente_http: TestClient, dados: dict[str, int]) -> None:
    entrar(cliente_http, "cliente@teste.local", SENHA)
    adicionar_item(cliente_http, dados["baunilha"], 2)
    pedido_pago = finalizar_pedido(cliente_http)
    assert pagar(cliente_http, pedido_pago).status_code == 303

    adicionar_item(cliente_http, dados["baunilha"], 1)
    finalizar_pedido(cliente_http)

    with TestClient(app) as admin:
        entrar(admin, "admin@teste.local", SENHA)
        pagina = admin.get("/admin/relatorio").text
    assert "R$ 28,00" in pagina
    assert "R$ 18,00" not in pagina
