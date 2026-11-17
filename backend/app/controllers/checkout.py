"""Checkout: endereço, frete e criação transacional do pedido."""

from __future__ import annotations

import json
from decimal import Decimal
from typing import Annotated
from urllib.request import urlopen

from fastapi import APIRouter, Depends, Form, Request
from fastapi.responses import Response
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.controllers.comum import (
    Sessao,
    avisar,
    avisar_codigo,
    redirecionar,
    renderizar,
    renderizar_form,
)
from app.core.acesso import exigir_usuario
from app.core.config import settings
from app.core.csrf import validar_csrf
from app.core.problemas import CATALOGO, ErroAplicacao
from app.models import (
    Endereco,
    HistoricoPedido,
    ItemPedido,
    Pagamento,
    Pedido,
    Produto,
    StatusPagamento,
    StatusPedido,
    Usuario,
)
from app.services.carrinho import Carrinho, definir, gravar_carrinho, ler_carrinho, remover
from app.services.carrinho_db import carregar_itens
from app.services.endereco import EnderecoValidado, validar_endereco
from app.services.identificador import codigo_pedido
from app.services.preco import calcular_frete, somar_itens
from app.services.validacao import normalizar_cep, normalizar_telefone

router = APIRouter(dependencies=[Depends(validar_csrf)])
VIACEP_URL = "https://viacep.com.br/ws/{cep}/json/"


def _consultar_cep(cep: str) -> dict[str, str]:
    """Consulta o ViaCEP e devolve só os campos usados pelo checkout."""
    try:
        with urlopen(VIACEP_URL.format(cep=cep), timeout=4) as resposta:  # noqa: S310
            dados = json.load(resposta)
    except (OSError, ValueError) as exc:
        raise ErroAplicacao("ERR-CHK-004") from exc
    if not isinstance(dados, dict) or dados.get("erro"):
        raise ErroAplicacao("ERR-CHK-005")
    return {
        "logradouro": str(dados.get("logradouro") or ""),
        "bairro": str(dados.get("bairro") or ""),
        "cidade": str(dados.get("localidade") or ""),
        "uf": str(dados.get("uf") or ""),
    }


def _alterar_item(banco: Session, carrinho: Carrinho, item: str) -> Carrinho:
    """Aplica mais/menos/remover sem sair do checkout."""
    acao, _, alvo = item.partition(":")
    if acao not in {"mais", "menos", "remover"} or not alvo.isdigit():
        raise ErroAplicacao("ERR-CAT-001")
    produto_id = int(alvo)
    if acao == "remover":
        return remover(carrinho, produto_id)
    if produto_id not in carrinho:
        raise ErroAplicacao("ERR-CAT-001")
    produto = banco.get(Produto, produto_id)
    if produto is None or produto.excluido_em is not None:
        raise ErroAplicacao("ERR-CAT-001")
    atual = carrinho.get(produto_id, 0)
    nova = atual + (1 if acao == "mais" else -1)
    return definir(carrinho, produto_id, nova, produto.estoque)


def _contexto(
    banco: Session,
    carrinho: dict[int, int],
) -> tuple[list[tuple[Produto, int]], Decimal, Decimal, Decimal, bool]:
    itens, ajustado = carregar_itens(banco, carrinho)
    subtotal = somar_itens((produto.preco, quantidade) for produto, quantidade in itens)
    frete = calcular_frete(
        subtotal,
        valor=settings.frete_valor,
        gratis_acima=settings.frete_gratis_acima,
    )
    return itens, subtotal, frete, subtotal + frete, ajustado


def _enderecos(banco: Session, usuario_id: int) -> list[Endereco]:
    return list(
        banco.scalars(
            select(Endereco)
            .where(Endereco.usuario_id == usuario_id)
            .order_by(Endereco.principal.desc(), Endereco.criado_em.desc())
        ).all()
    )


def _valores_checkout(
    usuario: Usuario,
    enderecos: list[Endereco],
    *,
    endereco_id: str = "",
) -> dict[str, str]:
    """Campos do formulário; o endereço salvo é escolhido explicitamente."""
    selecionado = endereco_id
    if not selecionado and enderecos:
        selecionado = str(enderecos[0].id)
    return {
        "endereco_id": selecionado,
        "cep": "",
        "logradouro": "",
        "numero": "",
        "complemento": "",
        "bairro": "",
        "cidade": "",
        "uf": "",
        "telefone": usuario.telefone or "",
    }


@router.get("/cep/{cep}")
def consultar_cep(cep: str) -> dict[str, str]:
    cep_limpo = normalizar_cep(cep)
    if cep_limpo is None:
        raise ErroAplicacao("ERR-CHK-002")
    return _consultar_cep(cep_limpo)


@router.get("/checkout")
def checkout_get(
    request: Request,
    banco: Sessao,
    usuario: Annotated[Usuario, Depends(exigir_usuario)],
) -> Response:
    carrinho = ler_carrinho(request.session)
    itens, subtotal, frete, total, ajustado = _contexto(banco, carrinho)
    mensagens = list(request.state.flash)
    if ajustado:
        gravar_carrinho(request.session, carrinho)
        mensagens.append(
            {
                "codigo": "ERR-CAR-002",
                "texto": CATALOGO["ERR-CAR-002"].detalhe,
                "tipo": "info",
            }
        )
    if not itens:
        avisar_codigo(request, "ERR-CAR-001")
        return redirecionar("/carrinho")
    enderecos = _enderecos(banco, usuario.id)
    return renderizar(
        request,
        "checkout/form.html",
        itens=itens,
        subtotal=subtotal,
        frete=frete,
        total=total,
        enderecos=enderecos,
        valores=_valores_checkout(usuario, enderecos),
        flash=mensagens,
    )


@router.post("/checkout")
def checkout_post(
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
    telefone: Annotated[str, Form()] = "",
    endereco_id: Annotated[str, Form()] = "",
    item: Annotated[str, Form()] = "",
) -> Response:
    enderecos = _enderecos(banco, usuario.id)
    valores = {
        "endereco_id": endereco_id,
        "cep": cep,
        "logradouro": logradouro,
        "numero": numero,
        "complemento": complemento,
        "bairro": bairro,
        "cidade": cidade,
        "uf": uf,
        "telefone": telefone,
    }
    carrinho = ler_carrinho(request.session)
    if item:
        try:
            carrinho = _alterar_item(banco, carrinho, item)
        except ErroAplicacao as erro:
            itens, subtotal, frete, total, _ = _contexto(banco, carrinho)
            return renderizar_form(
                request,
                "checkout/form.html",
                erro=erro,
                valores=valores,
                itens=itens,
                subtotal=subtotal,
                frete=frete,
                total=total,
                enderecos=enderecos,
            )
        gravar_carrinho(request.session, carrinho)
        itens, subtotal, frete, total, ajustado = _contexto(banco, carrinho)
        if ajustado:
            gravar_carrinho(request.session, carrinho)
        if not itens:
            avisar_codigo(request, "ERR-CAR-001")
            return redirecionar("/carrinho")
        if ajustado:
            return renderizar_form(
                request,
                "checkout/form.html",
                erro=ErroAplicacao("ERR-CAR-002"),
                valores=valores,
                itens=itens,
                subtotal=subtotal,
                frete=frete,
                total=total,
                enderecos=enderecos,
            )
        return renderizar(
            request,
            "checkout/form.html",
            valores=valores,
            itens=itens,
            subtotal=subtotal,
            frete=frete,
            total=total,
            enderecos=enderecos,
        )

    itens, subtotal, frete, total, ajustado = _contexto(banco, carrinho)
    if ajustado:
        gravar_carrinho(request.session, carrinho)
        if not itens:
            avisar_codigo(request, "ERR-CAR-001")
            return redirecionar("/carrinho")
        return renderizar_form(
            request,
            "checkout/form.html",
            erro=ErroAplicacao("ERR-CAR-002"),
            valores=valores,
            itens=itens,
            subtotal=subtotal,
            frete=frete,
            total=total,
            enderecos=enderecos,
        )

    try:
        telefone_limpo = normalizar_telefone(telefone)
        if telefone_limpo is None:
            raise ErroAplicacao(
                "ERR-CHK-001",
                campos={"telefone": "Informe DDD e telefone."},
            )
        endereco_salvo: Endereco | None = None
        if endereco_id and endereco_id != "novo":
            try:
                escolhido = int(endereco_id)
            except ValueError:
                raise ErroAplicacao(
                    "ERR-CHK-001",
                    campos={"cep": "Selecione um endereço válido."},
                ) from None
            endereco_salvo = banco.scalar(
                select(Endereco).where(
                    Endereco.id == escolhido,
                    Endereco.usuario_id == usuario.id,
                )
            )
            if endereco_salvo is None:
                raise ErroAplicacao(
                    "ERR-CHK-001",
                    campos={"cep": "Selecione um endereço válido."},
                )
            endereco_validado = EnderecoValidado(
                cep=endereco_salvo.cep,
                logradouro=endereco_salvo.logradouro,
                numero=endereco_salvo.numero,
                complemento=endereco_salvo.complemento,
                bairro=endereco_salvo.bairro,
                cidade=endereco_salvo.cidade,
                uf=endereco_salvo.uf,
            )
        else:
            endereco_validado = validar_endereco(
                cep=cep,
                logradouro=logradouro,
                numero=numero,
                complemento=complemento,
                bairro=bairro,
                cidade=cidade,
                uf=uf,
            )
        if not itens:
            raise ErroAplicacao("ERR-CAR-001")
    except ErroAplicacao as erro:
        return renderizar_form(
            request,
            "checkout/form.html",
            erro=erro,
            valores=valores,
            itens=itens,
            subtotal=subtotal,
            frete=frete,
            total=total,
            enderecos=enderecos,
        )

    pedido = Pedido(
        codigo=codigo_pedido(),
        cliente_id=usuario.id,
        status=StatusPedido.RECEBIDO,
        frete=frete,
        cep=endereco_validado.cep,
        logradouro=endereco_validado.logradouro,
        numero=endereco_validado.numero,
        complemento=endereco_validado.complemento,
        bairro=endereco_validado.bairro,
        cidade=endereco_validado.cidade,
        uf=endereco_validado.uf,
        telefone_contato=telefone_limpo,
    )
    banco.add(pedido)
    banco.flush()
    for produto, quantidade in itens:
        banco.add(
            ItemPedido(
                pedido_id=pedido.id,
                produto_id=produto.id,
                nome_produto=produto.nome,
                preco_unitario=produto.preco,
                quantidade=quantidade,
            )
        )
    banco.add(
        Pagamento(
            pedido_id=pedido.id,
            metodo=None,
            status=StatusPagamento.PENDENTE,
            valor=total,
        )
    )
    banco.add(
        HistoricoPedido(
            pedido_id=pedido.id,
            status=StatusPedido.RECEBIDO,
            usuario_id=usuario.id,
            observacao="Pedido criado no checkout.",
        )
    )

    if endereco_salvo is None:
        existente = banco.scalar(
            select(Endereco).where(
                Endereco.usuario_id == usuario.id,
                Endereco.cep == endereco_validado.cep,
                Endereco.numero == endereco_validado.numero,
            )
        )
        if existente is None:
            possui_principal = (
                banco.scalar(
                    select(func.count())
                    .select_from(Endereco)
                    .where(Endereco.usuario_id == usuario.id, Endereco.principal.is_(True))
                )
                or 0
            )
            banco.add(
                Endereco(
                    usuario_id=usuario.id,
                    cep=endereco_validado.cep,
                    logradouro=endereco_validado.logradouro,
                    numero=endereco_validado.numero,
                    complemento=endereco_validado.complemento,
                    bairro=endereco_validado.bairro,
                    cidade=endereco_validado.cidade,
                    uf=endereco_validado.uf,
                    principal=possui_principal == 0,
                )
            )
    if not usuario.telefone:
        persistido = banco.get(Usuario, usuario.id)
        if persistido is not None:
            persistido.telefone = telefone_limpo

    banco.commit()
    gravar_carrinho(request.session, {})
    avisar(request, f"Pedido #{pedido.referencia} criado. Escolha o pagamento.")
    return redirecionar(f"/pedidos/{pedido.codigo}/pagamento")
