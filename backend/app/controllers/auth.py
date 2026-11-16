"""Cadastro, login e logout."""

from __future__ import annotations

from typing import Annotated
from urllib.parse import urlencode

from fastapi import APIRouter, Depends, Form, Query, Request
from fastapi.responses import Response
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.controllers.comum import (
    Sessao,
    avisar,
    caminho_interno,
    redirecionar,
    renderizar,
    renderizar_form,
)
from app.core.csrf import validar_csrf
from app.core.limites import LimiteTentativas
from app.core.problemas import ErroAplicacao
from app.models import Papel, Usuario
from app.services.seguranca import (
    HASH_SEM_CONTA,
    email_valido,
    hash_senha,
    normalizar_email,
    senha_forte,
    verificar_senha,
)

router = APIRouter(dependencies=[Depends(validar_csrf)])
LIMITE_CONTA = LimiteTentativas(maximo=5, janela=15 * 60)
LIMITE_IP = LimiteTentativas(maximo=30, janela=15 * 60)


def _ip(request: Request) -> str:
    return request.client.host if request.client else "desconhecido"


@router.get("/cadastro")
def cadastro_get(
    request: Request,
    email: Annotated[str, Query()] = "",
) -> Response:
    if isinstance(getattr(request.state, "usuario", None), Usuario):
        return redirecionar("/")
    valores = {"email": normalizar_email(email)} if email else {}
    return renderizar(request, "auth/cadastro.html", valores=valores)


@router.post("/cadastro")
def cadastro_post(
    request: Request,
    banco: Sessao,
    nome: Annotated[str, Form()] = "",
    email: Annotated[str, Form()] = "",
    senha: Annotated[str, Form()] = "",
    confirmacao: Annotated[str, Form()] = "",
) -> Response:
    valores = {"nome": nome, "email": email}
    try:
        nome_limpo = nome.strip()
        email_limpo = normalizar_email(email)
        if not 2 <= len(nome_limpo) <= 120 or not email_valido(email_limpo):
            raise ErroAplicacao(
                "ERR-AUTH-005",
                campos={"nome": "Informe um nome válido.", "email": "Informe um e-mail válido."},
            )
        if not senha_forte(senha):
            raise ErroAplicacao("ERR-AUTH-003", campos={"senha": "Senha fora da política."})
        if senha != confirmacao:
            raise ErroAplicacao("ERR-AUTH-004", campos={"confirmacao": "As senhas não conferem."})
        existente = banco.scalar(select(Usuario).where(Usuario.email == email_limpo))
        if existente is not None:
            raise ErroAplicacao(
                "ERR-AUTH-002",
                campos={"email": "Este e-mail já está cadastrado."},
            )
        usuario = Usuario(
            nome=nome_limpo,
            email=email_limpo,
            senha_hash=hash_senha(senha),
            papel=Papel.CLIENTE,
            ativo=True,
        )
        banco.add(usuario)
        banco.commit()
        banco.refresh(usuario)
    except ErroAplicacao as erro:
        return renderizar_form(request, "auth/cadastro.html", erro=erro, valores=valores)
    except IntegrityError:
        banco.rollback()
        erro_email = ErroAplicacao(
            "ERR-AUTH-002",
            campos={"email": "Este e-mail já está cadastrado."},
        )
        return renderizar_form(request, "auth/cadastro.html", erro=erro_email, valores=valores)

    request.session.clear()
    request.session["usuario_id"] = usuario.id
    request.session["sessao_versao"] = usuario.sessao_versao
    avisar(request, "Conta criada com sucesso. Bem-vindo(a)!")
    return redirecionar("/")


@router.get("/login")
def login_get(
    request: Request,
    proximo: Annotated[str, Query(alias="next")] = "/",
) -> Response:
    if isinstance(getattr(request.state, "usuario", None), Usuario):
        return redirecionar("/")
    return renderizar(
        request,
        "auth/login.html",
        valores={},
        proximo=caminho_interno(proximo),
    )


@router.post("/login")
def login_post(
    request: Request,
    banco: Sessao,
    email: Annotated[str, Form()] = "",
    senha: Annotated[str, Form()] = "",
    proximo: Annotated[str, Form(alias="next")] = "/",
) -> Response:
    destino = caminho_interno(proximo)
    valores = {"email": email}
    ip = _ip(request)
    email_limpo = normalizar_email(email)
    chave_conta = f"{ip}:{email_limpo}"
    if LIMITE_CONTA.excedido(chave_conta) or LIMITE_IP.excedido(ip):
        return renderizar_form(
            request,
            "auth/login.html",
            erro=ErroAplicacao("ERR-AUTH-010"),
            valores=valores,
            proximo=destino,
        )
    try:
        usuario = banco.scalar(select(Usuario).where(Usuario.email == email_limpo))
        if usuario is None:
            verificar_senha(senha, HASH_SEM_CONTA)
            LIMITE_CONTA.registrar(chave_conta)
            LIMITE_IP.registrar(ip)
            return renderizar(
                request,
                "auth/login.html",
                status_code=401,
                valores=valores,
                proximo=destino,
                email_desconhecido=True,
                cadastro_url=f"/cadastro?{urlencode({'email': email_limpo})}",
            )
        if not verificar_senha(senha, usuario.senha_hash):
            raise ErroAplicacao(
                "ERR-AUTH-001",
                campos={
                    "email": "E-mail ou senha inválidos.",
                    "senha": "E-mail ou senha inválidos.",
                },
            )
        if not usuario.ativo:
            raise ErroAplicacao("ERR-AUTH-006")
    except ErroAplicacao as erro:
        if erro.codigo == "ERR-AUTH-001":
            LIMITE_CONTA.registrar(chave_conta)
            LIMITE_IP.registrar(ip)
        return renderizar_form(
            request,
            "auth/login.html",
            erro=erro,
            valores=valores,
            proximo=destino,
        )

    LIMITE_CONTA.limpar(chave_conta)
    request.session.clear()
    request.session["usuario_id"] = usuario.id
    request.session["sessao_versao"] = usuario.sessao_versao
    avisar(request, f"Bem-vindo(a), {usuario.nome}!")
    return redirecionar(destino)


@router.post("/logout")
def logout(request: Request, banco: Sessao) -> Response:
    usuario = getattr(request.state, "usuario", None)
    if isinstance(usuario, Usuario):
        persistido = banco.get(Usuario, usuario.id)
        if persistido is not None:
            persistido.sessao_versao += 1
            banco.commit()
    request.session.clear()
    avisar(request, "Sessão encerrada.", tipo="info")
    return redirecionar("/")
