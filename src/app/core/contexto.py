"""Contexto por requisição: usuário da sessão, flash e contador do carrinho."""

from __future__ import annotations

from collections.abc import Awaitable, Callable, MutableMapping
from uuid import uuid4

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.core.db import SessionLocal
from app.models import Usuario
from app.services.carrinho import ler_carrinho, quantidade_total


def _ler_flash(sessao: MutableMapping[str, object]) -> list[dict[str, str]]:
    bruto = sessao.pop("flash", [])
    if not isinstance(bruto, list):
        return []
    mensagens: list[dict[str, str]] = []
    for item in bruto:
        if isinstance(item, dict) and isinstance(item.get("texto"), str):
            mensagens.append(
                {
                    "codigo": str(item.get("codigo", "")),
                    "texto": str(item["texto"]),
                    "tipo": str(item.get("tipo", "info")),
                }
            )
    return mensagens


class ContextoMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        request.state.request_id = uuid4().hex[:12]
        request.state.usuario = None
        request.state.flash = []
        request.state.carrinho_quantidade = 0

        if request.url.path.startswith("/static"):
            return await call_next(request)

        sessao = request.session
        request.state.carrinho_quantidade = quantidade_total(ler_carrinho(sessao))
        request.state.flash = _ler_flash(sessao)

        identificador = sessao.get("usuario_id")
        if isinstance(identificador, int):
            with SessionLocal() as banco:
                usuario = banco.get(Usuario, identificador)
                if usuario is not None and usuario.ativo:
                    request.state.usuario = usuario
                else:
                    sessao.pop("usuario_id", None)

        return await call_next(request)
