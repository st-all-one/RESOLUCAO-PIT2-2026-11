"""Área do entregador: visibilidade e confirmação."""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.main import app
from tests.apoio import criar_pedido_pago, entrar, escalar, postar, token_csrf, url_pedido
from tests.conftest import SENHA


def _pedido_em_rota(cliente_http: TestClient, dados: dict[str, int]) -> int:
    entrar(cliente_http, "cliente@teste.local", SENHA)
    pedido_id = criar_pedido_pago(cliente_http, dados["baunilha"])
    pagina = f"/admin/pedidos/{pedido_id}"

    with TestClient(app) as admin:
        entrar(admin, "admin@teste.local", SENHA)
        resposta = postar(admin, f"{pagina}/status", {"destino": "em_preparo"}, pagina=pagina)
        assert resposta.status_code == 303
        resposta = postar(
            admin,
            f"{pagina}/status",
            {"destino": "saiu_entrega", "entregador_id": str(dados["entregador"])},
            pagina=pagina,
        )
        assert resposta.status_code == 303
    return pedido_id


def test_entregador_lista_e_confirma(cliente_http: TestClient, dados: dict[str, int]) -> None:
    pedido_id = _pedido_em_rota(cliente_http, dados)

    with TestClient(app) as entregador:
        entrar(entregador, "entregador@teste.local", SENHA)
        assert "Pedido #" in entregador.get("/entregas").text

        resposta = postar(
            entregador,
            f"/entregas/{pedido_id}/confirmar",
            {},
            pagina=f"/entregas/{pedido_id}",
        )
        assert resposta.status_code == 303
        assert "Nenhuma entrega em rota" in entregador.get("/entregas").text

    assert escalar("SELECT status FROM pedidos WHERE id=:id", id=pedido_id) == "entregue"
    assert "Entregue" in cliente_http.get(url_pedido(pedido_id)).text


def test_entregador_nao_ve_entrega_de_outro(
    cliente_http: TestClient, dados: dict[str, int]
) -> None:
    pedido_id = _pedido_em_rota(cliente_http, dados)

    with TestClient(app) as outro_entregador:
        entrar(outro_entregador, "entregador2@teste.local", SENHA)
        resposta = outro_entregador.get(
            f"/entregas/{pedido_id}",
            headers={"accept": "application/problem+json"},
        )
    assert resposta.status_code == 403
    assert resposta.json()["codigo"] == "ERR-ENT-001"


def test_entregador_nao_acessa_administracao(
    cliente_http: TestClient, dados: dict[str, int]
) -> None:
    with TestClient(app) as entregador:
        entrar(entregador, "entregador@teste.local", SENHA)
        resposta = entregador.get(
            "/admin/produtos",
            headers={"accept": "application/problem+json"},
        )
    assert resposta.status_code == 403
    assert resposta.json()["codigo"] == "ERR-AUTH-007"


def test_entregador_nao_confirma_entrega_alheia(
    cliente_http: TestClient, dados: dict[str, int]
) -> None:
    pedido_id = _pedido_em_rota(cliente_http, dados)

    with TestClient(app) as outro_entregador:
        entrar(outro_entregador, "entregador2@teste.local", SENHA)
        token = token_csrf(outro_entregador, "/")
        resposta = outro_entregador.post(
            f"/entregas/{pedido_id}/confirmar",
            data={"csrf_token": token},
            headers={"accept": "application/problem+json"},
            follow_redirects=False,
        )
    assert resposta.status_code == 403
    assert resposta.json()["codigo"] == "ERR-ENT-001"
    assert escalar("SELECT status FROM pedidos WHERE id=:id", id=pedido_id) == "saiu_entrega"
