"""Helpers compartilhados pelos controllers."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Request
from fastapi.responses import RedirectResponse, Response
from sqlalchemy.orm import Session

from app.core.db import obter_sessao
from app.core.problemas import CATALOGO, ErroAplicacao, Problema
from app.core.templating import contexto, templates

Sessao = Annotated[Session, Depends(obter_sessao)]


def renderizar(
    request: Request,
    nome: str,
    *,
    status_code: int = 200,
    **extra: object,
) -> Response:
    return templates.TemplateResponse(
        request,
        nome,
        contexto(request, **extra),
        status_code=status_code,
    )


def renderizar_form(
    request: Request,
    nome: str,
    *,
    erro: ErroAplicacao | None = None,
    **extra: object,
) -> Response:
    problema = Problema.de_erro(erro, request.url.path).para_dict() if erro else None
    return renderizar(
        request,
        nome,
        status_code=erro.status if erro else 200,
        erro=erro,
        problema_dict=problema,
        **extra,
    )


def redirecionar(url: str, *, status_code: int = 303) -> RedirectResponse:
    return RedirectResponse(url=url, status_code=status_code)


def caminho_interno(valor: str | None, padrao: str = "/") -> str:
    if not valor or not valor.startswith("/") or valor.startswith("//"):
        return padrao
    minusculo = valor.lower()
    if "\\" in valor or "%5c" in minusculo or "%2f" in minusculo:
        return padrao
    if any(ord(caractere) < 0x20 for caractere in valor):
        return padrao
    return valor


def _adicionar_flash(request: Request, entrada: dict[str, str]) -> None:
    atual = request.session.get("flash")
    lista: list[dict[str, str]] = atual if isinstance(atual, list) else []
    lista.append(entrada)
    request.session["flash"] = lista


def avisar(
    request: Request,
    texto: str,
    *,
    tipo: str = "sucesso",
    codigo: str = "",
) -> None:
    _adicionar_flash(request, {"codigo": codigo, "texto": texto, "tipo": tipo})


def avisar_codigo(
    request: Request,
    codigo: str,
    *,
    texto: str | None = None,
    tipo: str = "erro",
) -> None:
    definicao = CATALOGO[codigo]
    _adicionar_flash(
        request,
        {"codigo": codigo, "texto": texto or definicao.detalhe, "tipo": tipo},
    )
