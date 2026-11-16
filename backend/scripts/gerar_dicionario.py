"""Gera docs/05-dados/dicionario.md a partir do information_schema do MariaDB.

Falha com exit 1 se alguma coluna do banco não tiver descrição, garantindo que o
dicionário cubra 100% do schema. Uso:

    .venv/bin/python backend/scripts/gerar_dicionario.py
"""

from __future__ import annotations

import os
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Connection

DESTINO = Path(__file__).resolve().parents[2] / "docs" / "05-dados" / "dicionario.md"
URL_PADRAO = "mariadb+pymysql://cupcake:cupcake@127.0.0.1:3307/cupcake?charset=utf8mb4"

DESCRICOES: dict[str, dict[str, str]] = {
    "usuarios": {
        "id": "Identificador interno da conta.",
        "nome": "Nome de exibição da pessoa.",
        "email": "Identidade de login; normalizado em minúsculas.",
        "senha_hash": "Hash scrypt da senha com salt; nunca a senha em claro.",
        "telefone": "Telefone de contato com DDD, somente dígitos.",
        "papel": "Perfil de acesso do usuário.",
        "ativo": "Indica se a conta pode autenticar.",
        "criado_em": "Data e hora de criação da conta.",
        "atualizado_em": "Data e hora da última alteração.",
    },
    "categorias": {
        "id": "Identificador interno da categoria.",
        "nome": "Nome exibido na vitrine.",
        "slug": "Identificador textual usado na URL.",
        "ativo": "Indica se a categoria aparece na vitrine.",
        "criado_em": "Data e hora de criação.",
    },
    "produtos": {
        "id": "Identificador interno do produto.",
        "categoria_id": "Categoria à qual o produto pertence.",
        "nome": "Nome comercial do cupcake.",
        "slug": "Identificador textual usado na URL do detalhe.",
        "descricao": "Descrição comercial do produto.",
        "alergenicos": "Ingredientes alergênicos declarados.",
        "preco": "Preço unitário vigente em reais.",
        "estoque": "Quantidade disponível para venda.",
        "ativo": "Indica se o produto aparece na vitrine.",
        "criado_em": "Data e hora de criação.",
        "atualizado_em": "Data e hora da última alteração.",
    },
    "enderecos": {
        "id": "Identificador interno do endereço.",
        "usuario_id": "Dono do endereço.",
        "cep": "CEP com 8 dígitos, sem hífen.",
        "logradouro": "Rua, avenida ou praça.",
        "numero": "Número do imóvel.",
        "complemento": "Apartamento, bloco ou referência.",
        "bairro": "Bairro do endereço.",
        "cidade": "Cidade do endereço.",
        "uf": "Unidade federativa com 2 letras maiúsculas.",
        "principal": "Indica o endereço padrão do usuário.",
        "criado_em": "Data e hora de criação.",
    },
    "pedidos": {
        "id": "Identificador interno do pedido.",
        "cliente_id": "Cliente que realizou o pedido.",
        "entregador_id": "Entregador atribuído ao despacho.",
        "status": "Estado atual do pedido na máquina de estados.",
        "frete": "Valor do frete cobrado no momento do pedido.",
        "cep": "CEP do endereço de entrega (snapshot).",
        "logradouro": "Logradouro de entrega (snapshot).",
        "numero": "Número de entrega (snapshot).",
        "complemento": "Complemento de entrega (snapshot).",
        "bairro": "Bairro de entrega (snapshot).",
        "cidade": "Cidade de entrega (snapshot).",
        "uf": "UF de entrega (snapshot).",
        "telefone_contato": "Telefone para contato na entrega (snapshot).",
        "criado_em": "Data e hora da criação do pedido.",
        "atualizado_em": "Data e hora da última mudança de estado.",
    },
    "itens_pedido": {
        "id": "Identificador interno do item.",
        "pedido_id": "Pedido ao qual o item pertence.",
        "produto_id": "Produto comprado.",
        "nome_produto": "Nome do produto no momento da compra (snapshot).",
        "preco_unitario": "Preço unitário no momento da compra (snapshot).",
        "quantidade": "Quantidade comprada do produto.",
    },
    "pagamentos": {
        "id": "Identificador interno do pagamento.",
        "pedido_id": "Pedido pago; relação um para um.",
        "metodo": "Meio de pagamento escolhido.",
        "status": "Estado do pagamento.",
        "valor": "Montante autorizado no ato do pagamento.",
        "cartao_ultimos4": "Últimos 4 dígitos do cartão; nunca o número completo.",
        "codigo_autorizacao": "Código devolvido pela operadora simulada.",
        "criado_em": "Data e hora de criação do pagamento.",
        "atualizado_em": "Data e hora da última alteração.",
    },
    "historico_pedido": {
        "id": "Identificador interno do evento.",
        "pedido_id": "Pedido ao qual o evento se refere.",
        "status": "Status registrado no evento.",
        "usuario_id": "Quem provocou a transição.",
        "observacao": "Nota livre sobre a transição.",
        "criado_em": "Data e hora do evento.",
    },
}

DOMINIOS: dict[str, dict[str, str]] = {
    "usuarios": {
        "papel": "cliente | entregador | admin",
        "ativo": "0 = inativo, 1 = ativo",
    },
    "categorias": {"ativo": "0 = oculta, 1 = visível"},
    "produtos": {
        "preco": "> 0, duas casas decimais",
        "estoque": ">= 0",
        "ativo": "0 = oculto, 1 = visível",
    },
    "enderecos": {
        "cep": "8 dígitos",
        "uf": "2 letras maiúsculas",
        "principal": "0 = alternativo, 1 = padrão",
    },
    "pedidos": {
        "status": "recebido | em_preparo | saiu_entrega | entregue | cancelado",
        "frete": ">= 0",
        "uf": "2 letras maiúsculas",
    },
    "itens_pedido": {
        "preco_unitario": "> 0",
        "quantidade": "> 0",
    },
    "pagamentos": {
        "metodo": "pix | cartao",
        "status": "pendente | aprovado | recusado | estornado | cancelado",
        "valor": "> 0",
        "cartao_ultimos4": "4 dígitos quando metodo = cartao",
    },
    "historico_pedido": {
        "status": "recebido | em_preparo | saiu_entrega | entregue | cancelado",
    },
}


def _chaves(conexao: Connection) -> dict[tuple[str, str], list[str]]:
    resultado: dict[tuple[str, str], list[str]] = {}
    sql = text(
        """
        SELECT k.TABLE_NAME, k.COLUMN_NAME, k.CONSTRAINT_NAME, k.REFERENCED_TABLE_NAME,
               k.REFERENCED_COLUMN_NAME, t.CONSTRAINT_TYPE
        FROM information_schema.KEY_COLUMN_USAGE k
        JOIN information_schema.TABLE_CONSTRAINTS t
          ON t.CONSTRAINT_SCHEMA = k.CONSTRAINT_SCHEMA
         AND t.TABLE_NAME = k.TABLE_NAME
         AND t.CONSTRAINT_NAME = k.CONSTRAINT_NAME
        WHERE k.TABLE_SCHEMA = DATABASE()
        """
    )
    for linha in conexao.execute(sql):
        tabela, coluna, _nome, ref_tabela, ref_coluna, tipo = (str(v) for v in linha)
        marcas: list[str] = []
        if tipo == "PRIMARY KEY":
            marcas.append("PK")
        elif tipo == "UNIQUE":
            marcas.append("UQ")
        elif tipo == "FOREIGN KEY":
            marcas.append(f"FK → {ref_tabela}.{ref_coluna}")
        elif tipo == "INDEX":
            marcas.append("IDX")
        anterior = resultado.get((tabela, coluna), [])
        resultado[(tabela, coluna)] = anterior + [m for m in marcas if m not in anterior]
    return resultado


def _restricoes(conexao: Connection) -> dict[str, list[str]]:
    resultado: dict[str, list[str]] = {}
    sql = text(
        """
        SELECT tc.TABLE_NAME, cc.CONSTRAINT_NAME, cc.CHECK_CLAUSE
        FROM information_schema.TABLE_CONSTRAINTS tc
        JOIN information_schema.CHECK_CONSTRAINTS cc
          ON cc.CONSTRAINT_SCHEMA = tc.CONSTRAINT_SCHEMA
         AND cc.CONSTRAINT_NAME = tc.CONSTRAINT_NAME
        WHERE tc.TABLE_SCHEMA = DATABASE() AND tc.CONSTRAINT_TYPE = 'CHECK'
        ORDER BY tc.TABLE_NAME, cc.CONSTRAINT_NAME
        """
    )
    for linha in conexao.execute(sql):
        tabela, nome, clausula = (str(v) for v in linha)
        resultado.setdefault(tabela, []).append(f"`{nome}`: `{clausula}`")
    return resultado


def main() -> int:
    url = os.environ.get("DATABASE_URL", URL_PADRAO)
    motor = create_engine(url, pool_pre_ping=True)
    agora = datetime.now(ZoneInfo("America/Sao_Paulo")).strftime("%Y-%m-%d %H:%M")

    with motor.connect() as conexao:
        tabelas = [
            str(linha[0])
            for linha in conexao.execute(
                text(
                    """
                    SELECT TABLE_NAME FROM information_schema.TABLES
                    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_TYPE = 'BASE TABLE'
                    ORDER BY TABLE_NAME
                    """
                )
            )
        ]
        colunas = conexao.execute(
            text(
                """
                SELECT TABLE_NAME, COLUMN_NAME, COLUMN_TYPE, IS_NULLABLE,
                       COLUMN_DEFAULT, COLUMN_KEY, EXTRA
                FROM information_schema.COLUMNS
                WHERE TABLE_SCHEMA = DATABASE()
                ORDER BY TABLE_NAME, ORDINAL_POSITION
                """
            )
        ).all()
        chaves = _chaves(conexao)
        restricoes = _restricoes(conexao)

    faltantes = [
        f"{linha[0]!s}.{linha[1]!s}"
        for linha in colunas
        if str(linha[1]) not in DESCRICOES.get(str(linha[0]), {})
    ]
    if faltantes:
        print("Colunas sem descrição no dicionário:", ", ".join(faltantes), file=sys.stderr)
        return 1

    linhas: list[str] = [
        "# Dicionário de dados",
        "",
        (
            f"> Gerado automaticamente de `information_schema` em {agora}. "
            "Não editar à mão: rode `make dicionario`."
        ),
        "",
        "## Resumo",
        "",
        "| Tabela | Colunas | Restrições CHECK |",
        "|---|---|---|",
    ]
    for tabela in tabelas:
        total = sum(1 for linha in colunas if str(linha[0]) == tabela)
        linhas.append(f"| `{tabela}` | {total} | {len(restricoes.get(tabela, []))} |")

    for tabela in tabelas:
        linhas.extend(
            [
                "",
                f"## `{tabela}`",
                "",
                "| Coluna | Tipo | Nulo? | Default | Chave / Domínio | Descrição |",
                "|---|---|---|---|---|---|",
            ]
        )
        for linha in colunas:
            if str(linha[0]) != tabela:
                continue
            _t, coluna, tipo, nulo, padrao, _k, extra = linha
            marcas = list(chaves.get((tabela, str(coluna)), []))
            dominio = DOMINIOS.get(tabela, {}).get(str(coluna))
            if dominio:
                marcas.append(dominio)
            padrao_txt = "—" if padrao is None else f"`{padrao}`"
            if str(extra):
                padrao_txt = f"{padrao_txt} ({extra})"
            linhas.append(
                f"| `{coluna}` | `{tipo}` | {'sim' if str(nulo) == 'YES' else 'não'} | "
                f"{padrao_txt} | {' · '.join(marcas) or '—'} | "
                f"{DESCRICOES[tabela][str(coluna)]} |"
            )
        if restricoes.get(tabela):
            linhas.extend(["", "**Restrições CHECK:**", ""])
            linhas.extend(f"- {item}" for item in restricoes[tabela])

    DESTINO.parent.mkdir(parents=True, exist_ok=True)
    DESTINO.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    print(f"Dicionário gerado: {DESTINO} ({len(colunas)} colunas)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
