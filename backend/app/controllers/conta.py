"""Conta do usuário: dados cadastrais, senha e endereços de entrega."""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import Response
from sqlalchemy import select, update
from sqlalchemy.orm import Session

from app.controllers.comum import Sessao, avisar, redirecionar, renderizar, renderizar_form
from app.core.acesso import exigir_usuario
from app.core.csrf import validar_csrf
from app.core.problemas import ErroAplicacao
from app.models import Endereco, Usuario
from app.services.endereco import validar_endereco
from app.services.seguranca import (
    email_valido,
    hash_senha,
    normalizar_email,
    senha_forte,
    verificar_senha,
)
from app.services.validacao import normalizar_telefone

router = APIRouter(prefix="/conta", dependencies=[Depends(validar_csrf)])


def _enderecos(banco: Session, usuario_id: int) -> list[Endereco]:
    return list(
        banco.scalars(
            select(Endereco)
            .where(Endereco.usuario_id == usuario_id)
            .order_by(Endereco.principal.desc(), Endereco.criado_em.desc())
        ).all()
    )


def _valores(usuario: Usuario) -> dict[str, str]:
    return {
        "nome": usuario.nome,
        "email": usuario.email,
        "telefone": usuario.telefone or "",
    }


def _pagina_conta(
    request: Request,
    banco: Session,
    usuario: Usuario,
    *,
    erro: ErroAplicacao | None = None,
    valores: dict[str, str] | None = None,
    endereco_valores: dict[str, str] | None = None,
) -> Response:
    contexto = {
        "valores": valores or _valores(usuario),
        "enderecos": _enderecos(banco, usuario.id),
        "endereco_valores": endereco_valores or {},
    }
    if erro is not None:
        return renderizar_form(
            request,
            "conta/index.html",
            erro=erro,
            valores=contexto["valores"],
            enderecos=contexto["enderecos"],
            endereco_valores=contexto["endereco_valores"],
        )
    return renderizar(
        request,
        "conta/index.html",
        valores=contexto["valores"],
        enderecos=contexto["enderecos"],
        endereco_valores=contexto["endereco_valores"],
    )


@router.get("")
def conta_get(
    request: Request,
    banco: Sessao,
    usuario: Annotated[Usuario, Depends(exigir_usuario)],
) -> Response:
    return _pagina_conta(request, banco, usuario)


@router.post("/dados")
def atualizar_dados(
    request: Request,
    banco: Sessao,
    usuario: Annotated[Usuario, Depends(exigir_usuario)],
    nome: Annotated[str, Form()] = "",
    email: Annotated[str, Form()] = "",
    telefone: Annotated[str, Form()] = "",
) -> Response:
    valores = {"nome": nome, "email": email, "telefone": telefone}
    try:
        nome_limpo = nome.strip()
        email_limpo = normalizar_email(email)
        if not 2 <= len(nome_limpo) <= 120:
            raise ErroAplicacao("ERR-AUTH-005", campos={"nome": "Informe um nome válido."})
        if not email_valido(email_limpo):
            raise ErroAplicacao("ERR-AUTH-005", campos={"email": "Informe um e-mail válido."})
        telefone_limpo = normalizar_telefone(telefone) if telefone.strip() else None
        if telefone.strip() and telefone_limpo is None:
            raise ErroAplicacao(
                "ERR-CHK-001",
                campos={"telefone": "Informe DDD e telefone."},
            )
        conflito = banco.scalar(
            select(Usuario).where(Usuario.email == email_limpo, Usuario.id != usuario.id)
        )
        if conflito is not None:
            raise ErroAplicacao(
                "ERR-AUTH-002",
                campos={"email": "Este e-mail já está cadastrado."},
            )
        persistido = banco.get(Usuario, usuario.id)
        if persistido is None:
            raise ErroAplicacao("ERR-AUTH-009")
        persistido.nome = nome_limpo
        persistido.email = email_limpo
        persistido.telefone = telefone_limpo
        banco.commit()
    except ErroAplicacao as erro:
        return _pagina_conta(request, banco, usuario, erro=erro, valores=valores)
    avisar(request, "Dados da conta atualizados.")
    return redirecionar("/conta")


@router.post("/senha")
def alterar_senha(
    request: Request,
    banco: Sessao,
    usuario: Annotated[Usuario, Depends(exigir_usuario)],
    senha_atual: Annotated[str, Form()] = "",
    nova: Annotated[str, Form()] = "",
    confirmacao: Annotated[str, Form()] = "",
) -> Response:
    try:
        persistido = banco.get(Usuario, usuario.id)
        if persistido is None:
            raise ErroAplicacao("ERR-AUTH-009")
        if not verificar_senha(senha_atual, persistido.senha_hash):
            raise ErroAplicacao(
                "ERR-AUTH-001",
                campos={"senha_atual": "Senha atual incorreta."},
            )
        if not senha_forte(nova):
            raise ErroAplicacao("ERR-AUTH-003", campos={"nova": "Senha fora da política."})
        if nova != confirmacao:
            raise ErroAplicacao(
                "ERR-AUTH-004",
                campos={"confirmacao": "As senhas não conferem."},
            )
        persistido.senha_hash = hash_senha(nova)
        persistido.sessao_versao += 1
        banco.commit()
    except ErroAplicacao as erro:
        return _pagina_conta(request, banco, usuario, erro=erro)
    request.session["sessao_versao"] = persistido.sessao_versao
    avisar(request, "Senha alterada. As outras sessões foram encerradas.")
    return redirecionar("/conta")


@router.post("/enderecos")
def adicionar_endereco(
    request: Request,
    banco: Sessao,
    usuario: Annotated[Usuario, Depends(exigir_usuario)],
    cep: Annotated[str, Form()] = "",
    logradouro: Annotated[str, Form()] = "",
    numero: Annotated[str, Form()] = "",
    complemento: Annotated[str, Form()] = "",
    bairro: Annotated[str, Form()] = "",
    cidade: Annotated[str, Form()] = "",
    uf: Annotated[str, Form()] = "",
    principal: Annotated[str, Form()] = "",
) -> Response:
    valores = {
        "cep": cep,
        "logradouro": logradouro,
        "numero": numero,
        "complemento": complemento,
        "bairro": bairro,
        "cidade": cidade,
        "uf": uf,
    }
    try:
        validado = validar_endereco(**valores)
    except ErroAplicacao as erro:
        return _pagina_conta(
            request,
            banco,
            usuario,
            erro=erro,
            endereco_valores=valores,
        )
    existentes = _enderecos(banco, usuario.id)
    duplicado = any(
        endereco.cep == validado.cep and endereco.numero == validado.numero
        for endereco in existentes
    )
    if duplicado:
        avisar(request, "Este endereço já está salvo na sua conta.", tipo="info")
        return redirecionar("/conta")
    tornar_principal = principal == "on" or not existentes
    if tornar_principal:
        banco.execute(
            update(Endereco).where(Endereco.usuario_id == usuario.id).values(principal=False)
        )
    banco.add(
        Endereco(
            usuario_id=usuario.id,
            cep=validado.cep,
            logradouro=validado.logradouro,
            numero=validado.numero,
            complemento=validado.complemento,
            bairro=validado.bairro,
            cidade=validado.cidade,
            uf=validado.uf,
            principal=tornar_principal,
        )
    )
    banco.commit()
    avisar(request, "Endereço salvo.")
    return redirecionar("/conta")


def _endereco_do_usuario(banco: Session, usuario_id: int, endereco_id: int) -> Endereco:
    endereco = banco.scalar(
        select(Endereco).where(Endereco.id == endereco_id, Endereco.usuario_id == usuario_id)
    )
    if endereco is None:
        raise ErroAplicacao("ERR-END-001")
    return endereco


@router.post("/enderecos/{endereco_id}/principal")
def tornar_endereco_principal(
    request: Request,
    banco: Sessao,
    endereco_id: int,
    usuario: Annotated[Usuario, Depends(exigir_usuario)],
) -> Response:
    endereco = _endereco_do_usuario(banco, usuario.id, endereco_id)
    banco.execute(update(Endereco).where(Endereco.usuario_id == usuario.id).values(principal=False))
    endereco.principal = True
    banco.commit()
    avisar(request, "Endereço principal atualizado.")
    return redirecionar("/conta")


@router.post("/enderecos/{endereco_id}/remover")
def remover_endereco(
    request: Request,
    banco: Sessao,
    endereco_id: int,
    usuario: Annotated[Usuario, Depends(exigir_usuario)],
) -> Response:
    endereco = _endereco_do_usuario(banco, usuario.id, endereco_id)
    era_principal = endereco.principal
    banco.delete(endereco)
    banco.flush()
    if era_principal:
        novo_principal = banco.scalar(
            select(Endereco)
            .where(Endereco.usuario_id == usuario.id)
            .order_by(Endereco.criado_em.desc())
            .limit(1)
        )
        if novo_principal is not None:
            novo_principal.principal = True
    banco.commit()
    avisar(request, "Endereço removido.", tipo="info")
    return redirecionar("/conta")
