"""Carrinho: adicionar, atualizar, remover e visualizar."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import Response
from sqlalchemy import select

from app.controllers.comum import (
    Sessao,
    avisar,
    avisar_codigo,
    caminho_interno,
    redirecionar,
    renderizar,
)
from app.core.config import settings
from app.core.csrf import validar_csrf
from app.core.problemas import CATALOGO, ErroAplicacao
from app.models import Categoria, Produto
from app.services.carrinho import (
    adicionar,
    definir,
    gravar_carrinho,
    ler_carrinho,
    remover,
)
from app.services.carrinho_db import carregar_itens
from app.services.preco import calcular_frete, somar_itens

router = APIRouter(dependencies=[Depends(validar_csrf)])


@router.get("/carrinho")
def ver_carrinho(request: Request, banco: Sessao) -> Response:
    carrinho = ler_carrinho(request.session)
    itens, ajustado = carregar_itens(banco, carrinho)
    mensagens = list(request.state.flash)
    if ajustado:
        gravar_carrinho(request.session, carrinho)
        mensagens.append(
            {
                "codigo": "ERR-CAR-003",
                "texto": CATALOGO["ERR-CAR-003"].detalhe,
                "tipo": "info",
            }
        )
    subtotal = somar_itens((produto.preco, quantidade) for produto, quantidade in itens)
    frete = calcular_frete(
        subtotal,
        valor=settings.frete_valor,
        gratis_acima=settings.frete_gratis_acima,
    )
    return renderizar(
        request,
        "carrinho/carrinho.html",
        itens=itens,
        subtotal=subtotal,
        frete=frete,
        total=subtotal + frete,
        flash=mensagens,
    )


@router.post("/carrinho/adicionar")
def adicionar_item(
    request: Request,
    banco: Sessao,
    produto_id: Annotated[int, Form()],
    quantidade: Annotated[int, Form()] = 1,
    voltar: Annotated[str, Form()] = "",
) -> Response:
    produto = banco.scalar(
        select(Produto)
        .join(Produto.categoria)
        .where(
            Produto.id == produto_id,
            Produto.ativo.is_(True),
            Produto.excluido_em.is_(None),
            Categoria.ativo.is_(True),
        )
    )
    if produto is None:
        raise ErroAplicacao("ERR-CAT-001")
    carrinho = ler_carrinho(request.session)
    try:
        carrinho = adicionar(carrinho, produto_id, quantidade, produto.estoque)
    except ErroAplicacao as erro:
        avisar_codigo(request, erro.codigo, texto=erro.detalhe)
        return redirecionar(caminho_interno(voltar, f"/produtos/{produto.slug}"))
    except ValueError:
        avisar_codigo(request, "ERR-CAT-003")
        return redirecionar(caminho_interno(voltar, f"/produtos/{produto.slug}"))
    gravar_carrinho(request.session, carrinho)
    avisar(request, f"{produto.nome} adicionado ao carrinho.")
    return redirecionar(caminho_interno(voltar, "/carrinho"))


@router.post("/carrinho/atualizar")
def atualizar_item(
    request: Request,
    banco: Sessao,
    produto_id: Annotated[int, Form()],
    quantidade: Annotated[int, Form()],
) -> Response:
    produto = banco.get(Produto, produto_id)
    if produto is None or produto.excluido_em is not None:
        raise ErroAplicacao("ERR-CAT-001")
    carrinho = ler_carrinho(request.session)
    try:
        carrinho = definir(carrinho, produto_id, quantidade, produto.estoque)
    except ErroAplicacao as erro:
        avisar_codigo(request, erro.codigo, texto=erro.detalhe)
        return redirecionar("/carrinho")
    gravar_carrinho(request.session, carrinho)
    return redirecionar("/carrinho")


@router.post("/carrinho/remover")
def remover_item(
    request: Request,
    produto_id: Annotated[int, Form()],
) -> Response:
    carrinho = remover(ler_carrinho(request.session), produto_id)
    gravar_carrinho(request.session, carrinho)
    avisar(request, "Item removido do carrinho.", tipo="info")
    return redirecionar("/carrinho")
