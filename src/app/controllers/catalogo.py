"""Vitrine, busca, filtro por categoria e detalhe do produto."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import Response
from sqlalchemy import or_, select

from app.controllers.comum import Sessao, renderizar
from app.core.csrf import validar_csrf
from app.core.problemas import ErroAplicacao
from app.models import Categoria, Produto

router = APIRouter(dependencies=[Depends(validar_csrf)])


@router.get("/")
def vitrine(
    request: Request,
    banco: Sessao,
    q: Annotated[str, Query(max_length=120)] = "",
    categoria: Annotated[str, Query(max_length=80)] = "",
) -> Response:
    termo = q.strip()
    categorias = list(
        banco.scalars(
            select(Categoria).where(Categoria.ativo.is_(True)).order_by(Categoria.nome)
        ).all()
    )
    consulta = (
        select(Produto)
        .join(Produto.categoria)
        .where(Produto.ativo.is_(True), Categoria.ativo.is_(True))
    )
    if termo:
        consulta = consulta.where(
            or_(
                Produto.nome.icontains(termo, autoescape=True),
                Produto.descricao.icontains(termo, autoescape=True),
            )
        )
    if categoria:
        consulta = consulta.where(Categoria.slug == categoria)
    produtos = list(banco.scalars(consulta.order_by(Produto.nome)).all())
    return renderizar(
        request,
        "catalogo/vitrine.html",
        produtos=produtos,
        categorias=categorias,
        termo=termo,
        categoria_selecionada=categoria,
    )


@router.get("/produtos/{slug}")
def detalhe_produto(request: Request, banco: Sessao, slug: str) -> Response:
    produto = banco.scalar(
        select(Produto)
        .join(Produto.categoria)
        .where(
            Produto.slug == slug,
            Produto.ativo.is_(True),
            Categoria.ativo.is_(True),
        )
    )
    if produto is None:
        raise ErroAplicacao("ERR-CAT-001")
    return renderizar(request, "catalogo/detalhe.html", produto=produto)
