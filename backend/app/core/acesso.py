"""Autorização: sessão obrigatória, papéis e redirecionamento ao login."""

from __future__ import annotations

from collections.abc import Callable
from urllib.parse import quote

from fastapi import Request

from app.core.problemas import ErroAplicacao
from app.models import Usuario


class RedirecionarParaLogin(Exception):
    def __init__(self, destino: str) -> None:
        self.destino = destino
        super().__init__(destino)


def exigir_usuario(request: Request) -> Usuario:
    usuario = getattr(request.state, "usuario", None)
    if not isinstance(usuario, Usuario):
        raise RedirecionarParaLogin(f"/login?next={quote(request.url.path)}")
    return usuario


def exigir_papel(*papeis: str) -> Callable[[Request], Usuario]:
    def dependencia(request: Request) -> Usuario:
        usuario = exigir_usuario(request)
        if usuario.papel not in papeis:
            raise ErroAplicacao("ERR-AUTH-007")
        return usuario

    return dependencia
