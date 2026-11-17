"""Ponto de entrada: app factory, middleware, Problem Details e health check."""

from __future__ import annotations

import logging
from collections.abc import AsyncIterator, Awaitable, Callable
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import RedirectResponse, Response
from sqlalchemy import text
from sqlalchemy.exc import OperationalError
from starlette.exceptions import HTTPException as StarletteHTTPException
from starlette.middleware.sessions import SessionMiddleware
from starlette.staticfiles import StaticFiles

from app.controllers import (
    admin,
    auth,
    carrinho,
    catalogo,
    checkout,
    conta,
    entregas,
    pagamento,
    pedidos,
)
from app.core.acesso import RedirecionarParaLogin
from app.core.config import settings
from app.core.contexto import ContextoMiddleware
from app.core.db import engine
from app.core.partida import validar_admin_inicial
from app.core.problemas import ErroAplicacao, Problema, prefere_json, resposta_json
from app.core.templating import contexto, templates
from app.models import Base  # noqa: F401  (registra os mapeadores)

logger = logging.getLogger("cupcake")
DIRETORIO_ESTATICOS = Path(__file__).resolve().parent / "static"


def _pagina_problema(
    request: Request,
    problema: Problema,
    *,
    headers: dict[str, str] | None = None,
) -> Response:
    return templates.TemplateResponse(
        request,
        "erros/problema.html",
        contexto(request, problema=problema, problema_dict=problema.para_dict()),
        status_code=problema.status,
        headers=headers,
    )


@asynccontextmanager
async def ciclo_vida(_: FastAPI) -> AsyncIterator[None]:
    validar_admin_inicial()
    yield


def criar_app() -> FastAPI:
    app = FastAPI(
        title="Cupcake Gourmet",
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
        lifespan=ciclo_vida,
    )

    # A ordem importa: o SessionMiddleware precisa envolver o ContextoMiddleware.
    app.add_middleware(ContextoMiddleware)
    usa_https = settings.session_cookie_secure or settings.app_base_url.startswith("https://")
    app.add_middleware(
        SessionMiddleware,
        secret_key=settings.app_secret,
        session_cookie="cupcake_sessao",
        max_age=settings.session_max_age,
        same_site="lax",
        https_only=usa_https,
    )
    app.mount(
        "/static",
        StaticFiles(directory=str(DIRETORIO_ESTATICOS)),
        name="static",
    )
    settings.diretorio_midias.mkdir(parents=True, exist_ok=True)
    app.mount(
        "/midia",
        StaticFiles(directory=str(settings.diretorio_midias)),
        name="midia",
    )
    app.include_router(auth.router)
    app.include_router(catalogo.router)
    app.include_router(carrinho.router)
    app.include_router(checkout.router)
    app.include_router(conta.router)
    app.include_router(pagamento.router)
    app.include_router(pedidos.router)
    app.include_router(admin.router)
    app.include_router(entregas.router)

    @app.middleware("http")
    async def cabecalhos_seguranca(
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        resposta: Response = await call_next(request)
        resposta.headers.setdefault("X-Content-Type-Options", "nosniff")
        resposta.headers.setdefault("X-Frame-Options", "DENY")
        resposta.headers.setdefault("Referrer-Policy", "same-origin")
        resposta.headers.setdefault(
            "Permissions-Policy",
            "camera=(), geolocation=(), microphone=()",
        )
        resposta.headers.setdefault(
            "Content-Security-Policy",
            "default-src 'self'; base-uri 'self'; form-action 'self'; "
            "frame-ancestors 'none'; img-src 'self' data:; "
            "object-src 'none'; script-src 'self'; style-src 'self'",
        )
        if resposta.headers.get("content-type", "").startswith("text/html"):
            # Impede a Cloudflare de injetar o beacon de Web Analytics no HTML.
            # O beacon e bloqueado por protecao contra rastreamento e gera erros
            # de CORS/SRI no console; a aplicacao nao usa esse script.
            resposta.headers.setdefault("Cache-Control", "no-transform")
        if settings.session_cookie_secure or settings.app_base_url.startswith("https://"):
            resposta.headers.setdefault(
                "Strict-Transport-Security",
                "max-age=31536000; includeSubDomains",
            )
        return resposta

    @app.exception_handler(ErroAplicacao)
    async def tratar_erro_aplicacao(request: Request, exc: ErroAplicacao) -> Response:
        problema = Problema.de_erro(exc, request.url.path)
        if prefere_json(request):
            return resposta_json(problema)
        return _pagina_problema(request, problema)

    @app.exception_handler(RedirecionarParaLogin)
    async def tratar_login(request: Request, exc: RedirecionarParaLogin) -> Response:
        if prefere_json(request):
            return resposta_json(
                Problema.generico(
                    codigo="ERR-AUTH-009",
                    status=401,
                    instance=request.url.path,
                    detalhe="Autenticação necessária.",
                )
            )
        return RedirectResponse(url=exc.destino, status_code=303)

    @app.exception_handler(RequestValidationError)
    async def tratar_validacao(
        request: Request,
        exc: RequestValidationError,
    ) -> Response:
        campos: dict[str, str] = {}
        for erro in exc.errors():
            local = erro.get("loc", ())
            if isinstance(local, tuple) and local:
                campos[str(local[-1])] = "Valor inválido."
        problema = Problema.generico(
            codigo="ERR-VAL-001",
            status=422,
            instance=request.url.path,
            campos=campos,
        )
        if prefere_json(request):
            return resposta_json(problema)
        return _pagina_problema(request, problema)

    @app.exception_handler(StarletteHTTPException)
    async def tratar_http(request: Request, exc: StarletteHTTPException) -> Response:
        status = exc.status_code
        if status == 404:
            problema = Problema.generico(
                codigo="ERR-SYS-003",
                status=404,
                instance=request.url.path,
            )
        elif status in (401, 403):
            problema = Problema.generico(
                codigo="ERR-AUTH-007" if status == 403 else "ERR-AUTH-009",
                status=status,
                instance=request.url.path,
            )
        elif status == 405:
            problema = Problema.generico(
                codigo="ERR-SYS-004",
                status=405,
                instance=request.url.path,
                detalhe="Este endereço não aceita o método usado.",
            )
        else:
            problema = Problema.generico(
                codigo="ERR-SYS-001" if status >= 500 else "ERR-VAL-001",
                status=status,
                instance=request.url.path,
                detalhe="A requisição não pôde ser processada.",
            )
        cabecalhos = dict(exc.headers or {})
        if prefere_json(request):
            return resposta_json(problema, headers=cabecalhos)
        return _pagina_problema(request, problema, headers=cabecalhos)

    @app.exception_handler(OperationalError)
    async def tratar_banco(request: Request, exc: OperationalError) -> Response:
        logger.error(
            "banco_indisponivel request_id=%s path=%s",
            getattr(request.state, "request_id", ""),
            request.url.path,
            exc_info=exc,
        )
        problema = Problema.generico(
            codigo="ERR-SYS-002",
            status=503,
            instance=request.url.path,
        )
        if prefere_json(request):
            return resposta_json(problema)
        return _pagina_problema(request, problema)

    @app.exception_handler(Exception)
    async def tratar_inesperado(request: Request, exc: Exception) -> Response:
        logger.error(
            "erro_inesperado request_id=%s path=%s",
            getattr(request.state, "request_id", ""),
            request.url.path,
            exc_info=exc,
        )
        problema = Problema.generico(
            codigo="ERR-SYS-001",
            status=500,
            instance=request.url.path,
        )
        if prefere_json(request):
            return resposta_json(problema)
        return _pagina_problema(request, problema)

    @app.get("/health", include_in_schema=False)
    def health() -> dict[str, str]:
        with engine.connect() as conexao:
            conexao.execute(text("SELECT 1"))
        return {"status": "ok", "db": "ok"}

    return app


app = criar_app()
