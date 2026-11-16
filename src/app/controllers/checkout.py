"""Checkout: endereço, frete e criação transacional do pedido."""

from __future__ import annotations

from decimal import Decimal
from typing import Annotated

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
from app.core.problemas import ErroAplicacao
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
from app.services.carrinho import gravar_carrinho, ler_carrinho
from app.services.carrinho_db import carregar_itens
from app.services.preco import calcular_frete, somar_itens
from app.services.validacao import normalizar_cep, normalizar_telefone, normalizar_uf, texto

router = APIRouter(dependencies=[Depends(validar_csrf)])


def _contexto(
    banco: Session,
    carrinho: dict[int, int],
) -> tuple[list[tuple[Produto, int]], Decimal, Decimal, Decimal]:
    itens, _ajustado = carregar_itens(banco, carrinho)
    subtotal = somar_itens((produto.preco, quantidade) for produto, quantidade in itens)
    frete = calcular_frete(
        subtotal,
        valor=settings.frete_valor,
        gratis_acima=settings.frete_gratis_acima,
    )
    return itens, subtotal, frete, subtotal + frete


@router.get("/checkout")
def checkout_get(
    request: Request,
    banco: Sessao,
    usuario: Annotated[Usuario, Depends(exigir_usuario)],
) -> Response:
    carrinho = ler_carrinho(request.session)
    itens, subtotal, frete, total = _contexto(banco, carrinho)
    if not itens:
        avisar_codigo(request, "ERR-CAR-001")
        return redirecionar("/carrinho")
    endereco = banco.scalar(
        select(Endereco)
        .where(Endereco.usuario_id == usuario.id)
        .order_by(Endereco.principal.desc(), Endereco.criado_em.desc())
        .limit(1)
    )
    valores: dict[str, str] = {
        "cep": endereco.cep if endereco else "",
        "logradouro": endereco.logradouro if endereco else "",
        "numero": endereco.numero if endereco else "",
        "complemento": (endereco.complemento or "") if endereco else "",
        "bairro": endereco.bairro if endereco else "",
        "cidade": endereco.cidade if endereco else "",
        "uf": endereco.uf if endereco else "",
        "telefone": usuario.telefone or "",
    }
    return renderizar(
        request,
        "checkout/form.html",
        itens=itens,
        subtotal=subtotal,
        frete=frete,
        total=total,
        valores=valores,
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
) -> Response:
    valores = {
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
    itens, subtotal, frete, total = _contexto(banco, carrinho)

    try:
        cep_limpo = normalizar_cep(cep)
        if cep_limpo is None:
            raise ErroAplicacao("ERR-CHK-002", campos={"cep": "Informe 8 dígitos."})
        uf_limpa = normalizar_uf(uf)
        if uf_limpa is None:
            raise ErroAplicacao("ERR-CHK-003", campos={"uf": "Informe a UF com 2 letras."})
        telefone_limpo = normalizar_telefone(telefone)
        if telefone_limpo is None:
            raise ErroAplicacao(
                "ERR-CHK-001",
                campos={"telefone": "Informe DDD e telefone."},
            )
        logradouro_limpo = texto(logradouro, maximo=160)
        numero_limpo = texto(numero, maximo=20)
        bairro_limpo = texto(bairro, maximo=80)
        cidade_limpa = texto(cidade, maximo=80)
        if (
            logradouro_limpo is None
            or numero_limpo is None
            or bairro_limpo is None
            or cidade_limpa is None
        ):
            faltando = {
                nome: "Campo obrigatório."
                for nome, valor in (
                    ("logradouro", logradouro_limpo),
                    ("numero", numero_limpo),
                    ("bairro", bairro_limpo),
                    ("cidade", cidade_limpa),
                )
                if valor is None
            }
            raise ErroAplicacao("ERR-CHK-001", campos=faltando)
        complemento_limpo = complemento.strip() or None
        if complemento_limpo is not None and len(complemento_limpo) > 80:
            raise ErroAplicacao(
                "ERR-CHK-001",
                campos={"complemento": "Máximo de 80 caracteres."},
            )
        if not itens:
            raise ErroAplicacao("ERR-CAR-001")
        for produto, quantidade in itens:
            if quantidade > produto.estoque:
                raise ErroAplicacao(
                    "ERR-CAR-002",
                    campos={"quantidade": f"Estoque insuficiente para {produto.nome}."},
                )
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
        )

    pedido = Pedido(
        cliente_id=usuario.id,
        status=StatusPedido.RECEBIDO,
        frete=frete,
        cep=cep_limpo,
        logradouro=logradouro_limpo,
        numero=numero_limpo,
        complemento=complemento_limpo,
        bairro=bairro_limpo,
        cidade=cidade_limpa,
        uf=uf_limpa,
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

    existente = banco.scalar(
        select(Endereco).where(
            Endereco.usuario_id == usuario.id,
            Endereco.cep == cep_limpo,
            Endereco.numero == numero_limpo,
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
                cep=cep_limpo,
                logradouro=logradouro_limpo,
                numero=numero_limpo,
                complemento=complemento_limpo,
                bairro=bairro_limpo,
                cidade=cidade_limpa,
                uf=uf_limpa,
                principal=possui_principal == 0,
            )
        )
    if not usuario.telefone:
        usuario.telefone = telefone_limpo

    banco.commit()
    gravar_carrinho(request.session, {})
    avisar(request, f"Pedido #{pedido.id} criado. Escolha o pagamento.")
    return redirecionar(f"/pedidos/{pedido.id}/pagamento")
