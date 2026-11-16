"""Token CSRF e validação de mutações por formulário."""

from __future__ import annotations

import secrets

from fastapi import Request

from app.core.problemas import ErroAplicacao

CHAVE = "csrf_token"
METODOS_MUTANTES = frozenset({"POST", "PUT", "PATCH", "DELETE"})


def obter_token(request: Request) -> str:
    """Devolve o token da sessão, criando-o na primeira chamada."""
    token = request.session.get(CHAVE)
    if isinstance(token, str) and token:
        return token
    novo = secrets.token_urlsafe(32)
    request.session[CHAVE] = novo
    return novo


async def validar_csrf(request: Request) -> None:
    """Dependência de router: valida o token em toda mutação."""
    if request.method not in METODOS_MUTANTES:
        return
    tipo = request.headers.get("content-type", "")
    if not tipo.startswith(("application/x-www-form-urlencoded", "multipart/form-data")):
        raise ErroAplicacao("ERR-AUTH-008")
    formulario = await request.form()
    enviado = formulario.get(CHAVE)
    esperado = request.session.get(CHAVE)
    if (
        not isinstance(enviado, str)
        or not isinstance(esperado, str)
        or not esperado
        or not secrets.compare_digest(enviado, esperado)
    ):
        raise ErroAplicacao("ERR-AUTH-008")
