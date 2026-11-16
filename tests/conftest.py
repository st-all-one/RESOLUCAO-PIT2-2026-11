"""Fixtures da suíte: banco de teste, dados controlados e cliente HTTP."""

from __future__ import annotations

import os
from collections.abc import Iterator
from decimal import Decimal
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
os.environ.setdefault("APP_ENV", "test")
os.environ.setdefault("APP_SECRET", "segredo-de-teste-com-32-caracteres")
os.environ["DATABASE_URL"] = os.environ.get(
    "TEST_DATABASE_URL",
    "mariadb+pymysql://cupcake:cupcake@127.0.0.1:3307/cupcake_test?charset=utf8mb4",
)

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.db import engine
from app.main import app
from app.models import Categoria, Produto, Usuario
from app.services.seguranca import hash_senha

SENHA = "Senha@123"
HASH = hash_senha(SENHA)
TABELAS = (
    "historico_pedido",
    "pagamentos",
    "itens_pedido",
    "pedidos",
    "enderecos",
    "produtos",
    "categorias",
    "usuarios",
)


def _comandos_sql(caminho: Path) -> list[str]:
    linhas = [
        linha
        for linha in caminho.read_text(encoding="utf-8").splitlines()
        if not linha.strip().startswith("--")
    ]
    return [comando.strip() for comando in "\n".join(linhas).split(";") if comando.strip()]


@pytest.fixture(scope="session", autouse=True)
def esquema() -> None:
    """Recria o schema no banco de teste uma vez por sessão."""
    with engine.begin() as conexao:
        for comando in _comandos_sql(RAIZ / "db" / "schema.sql"):
            conexao.exec_driver_sql(comando)


@pytest.fixture(autouse=True)
def banco_limpo(esquema: None) -> None:
    """Zera os dados antes de cada teste para isolamento."""
    with engine.begin() as conexao:
        conexao.exec_driver_sql("SET FOREIGN_KEY_CHECKS = 0")
        for tabela in TABELAS:
            conexao.exec_driver_sql(f"TRUNCATE TABLE {tabela}")
        conexao.exec_driver_sql("SET FOREIGN_KEY_CHECKS = 1")


def _produto(
    categoria_id: int,
    *,
    nome: str,
    slug: str,
    preco: str,
    estoque: int,
    ativo: bool = True,
) -> Produto:
    return Produto(
        categoria_id=categoria_id,
        nome=nome,
        slug=slug,
        descricao=f"{nome} preparado na hora.",
        alergenicos="Leite, glúten e ovos.",
        preco=Decimal(preco),
        estoque=estoque,
        ativo=ativo,
    )


@pytest.fixture
def dados() -> dict[str, int]:
    """Usuários, categorias e produtos mínimos para os cenários."""
    with Session(engine) as sessao:
        usuarios = {
            "admin": Usuario(
                nome="Admin Teste",
                email="admin@teste.local",
                senha_hash=HASH,
                papel="admin",
                ativo=True,
            ),
            "cliente": Usuario(
                nome="Cliente Teste",
                email="cliente@teste.local",
                senha_hash=HASH,
                papel="cliente",
                ativo=True,
            ),
            "outro": Usuario(
                nome="Outro Cliente",
                email="outro@teste.local",
                senha_hash=HASH,
                papel="cliente",
                ativo=True,
            ),
            "entregador": Usuario(
                nome="Entregador Teste",
                email="entregador@teste.local",
                senha_hash=HASH,
                papel="entregador",
                ativo=True,
            ),
            "entregador2": Usuario(
                nome="Entregador Dois",
                email="entregador2@teste.local",
                senha_hash=HASH,
                papel="entregador",
                ativo=True,
            ),
        }
        sessao.add_all(usuarios.values())
        sessao.flush()

        tradicionais = Categoria(nome="Tradicionais", slug="tradicionais")
        veganos = Categoria(nome="Veganos", slug="veganos")
        sessao.add_all([tradicionais, veganos])
        sessao.flush()

        produtos = {
            "baunilha": _produto(
                tradicionais.id,
                nome="Cupcake Baunilha",
                slug="cupcake-baunilha",
                preco="10.00",
                estoque=5,
            ),
            "chocolate": _produto(
                tradicionais.id,
                nome="Cupcake Chocolate",
                slug="cupcake-chocolate",
                preco="20.00",
                estoque=2,
            ),
            "vegano": _produto(
                veganos.id,
                nome="Cupcake Vegano",
                slug="cupcake-vegano",
                preco="30.00",
                estoque=1,
            ),
            "inativo": _produto(
                tradicionais.id,
                nome="Cupcake Inativo",
                slug="cupcake-inativo",
                preco="5.00",
                estoque=10,
                ativo=False,
            ),
            "festa": _produto(
                tradicionais.id,
                nome="Cupcake Festa",
                slug="cupcake-festa",
                preco="130.00",
                estoque=1,
            ),
        }
        sessao.add_all(produtos.values())
        sessao.flush()

        resultado = {chave: usuario.id for chave, usuario in usuarios.items()}
        resultado |= {chave: produto.id for chave, produto in produtos.items()}
        resultado["tradicionais"] = tradicionais.id
        resultado["veganos"] = veganos.id
        sessao.commit()
    return resultado


@pytest.fixture
def cliente_http() -> Iterator[TestClient]:
    with TestClient(app) as cliente:
        yield cliente
