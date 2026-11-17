"""Administração: categorias, produtos, pedidos, relatório e usuários."""

from __future__ import annotations

from datetime import UTC, date, datetime, time
from decimal import Decimal, InvalidOperation
from typing import Annotated
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, File, Form, Query, Request, UploadFile
from fastapi.responses import Response
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.controllers.comum import (
    Sessao,
    avisar,
    avisar_codigo,
    redirecionar,
    renderizar,
    renderizar_form,
)
from app.core.acesso import exigir_papel, exigir_usuario
from app.core.csrf import validar_csrf
from app.core.problemas import ErroAplicacao
from app.models import (
    Categoria,
    ItemPedido,
    Pagamento,
    Papel,
    Pedido,
    Produto,
    StatusPagamento,
    StatusPedido,
    Usuario,
)
from app.services import midia
from app.services.operacoes import cancelar_pedido, registrar_historico
from app.services.pedido import transicoes_disponiveis, validar_transicao
from app.services.slug import gerar_slug
from app.services.validacao import texto

router = APIRouter(
    prefix="/admin",
    dependencies=[Depends(validar_csrf), Depends(exigir_papel(Papel.ADMIN))],
)


def _produto(banco: Session, produto_id: int) -> Produto:
    produto = banco.get(Produto, produto_id)
    if produto is None:
        raise ErroAplicacao("ERR-CAT-001")
    return produto


def _validar_produto(
    banco: Session,
    *,
    nome: str,
    categoria_id: int,
    descricao: str,
    alergenicos: str,
    preco: str,
    estoque: str,
    produto_id: int | None = None,
) -> tuple[str, Categoria, str, str, Decimal, int, str]:
    nome_limpo = texto(nome, minimo=2, maximo=120)
    descricao_limpa = texto(descricao, minimo=1, maximo=2000)
    alergenicos_limpos = texto(alergenicos, minimo=1, maximo=255)
    if nome_limpo is None or descricao_limpa is None or alergenicos_limpos is None:
        campos: dict[str, str] = {}
        if nome_limpo is None:
            campos["nome"] = "Entre 2 e 120 caracteres."
        if descricao_limpa is None:
            campos["descricao"] = "Descrição obrigatória."
        if alergenicos_limpos is None:
            campos["alergenicos"] = "Informe os alergênicos."
        raise ErroAplicacao("ERR-VAL-001", campos=campos)
    categoria = banco.get(Categoria, categoria_id)
    if categoria is None:
        raise ErroAplicacao("ERR-VAL-001", campos={"categoria_id": "Selecione uma categoria."})
    try:
        preco_dec = Decimal(preco.strip().replace(",", ".")).quantize(Decimal("0.01"))
    except (InvalidOperation, ValueError):
        raise ErroAplicacao("ERR-ADM-003") from None
    if preco_dec <= 0:
        raise ErroAplicacao("ERR-ADM-003")
    if preco_dec > Decimal("99999999.99"):
        raise ErroAplicacao("ERR-ADM-003", detalhe="Preço acima do limite.")
    try:
        estoque_int = int(estoque)
    except (TypeError, ValueError):
        raise ErroAplicacao("ERR-ADM-004") from None
    if estoque_int < 0:
        raise ErroAplicacao("ERR-ADM-004")
    slug = gerar_slug(nome_limpo)
    consulta_conflito = select(Produto).where(Produto.slug == slug)
    if produto_id is not None:
        consulta_conflito = consulta_conflito.where(Produto.id != produto_id)
    conflito = banco.scalar(consulta_conflito)
    if conflito is not None:
        raise ErroAplicacao(
            "ERR-ADM-008",
            campos={"nome": "Já existe um produto com esse nome."},
        )
    return nome_limpo, categoria, descricao_limpa, alergenicos_limpos, preco_dec, estoque_int, slug


@router.get("")
def raiz() -> Response:
    return redirecionar("/admin/produtos")


# ------------------------------------------------------------------ produtos
@router.get("/produtos")
def listar_produtos(
    request: Request,
    banco: Sessao,
    lixeira: Annotated[int, Query(ge=0, le=1)] = 0,
) -> Response:
    filtro = Produto.excluido_em.is_not(None) if lixeira else Produto.excluido_em.is_(None)
    produtos = list(
        banco.scalars(
            select(Produto)
            .options(selectinload(Produto.categoria))
            .where(filtro)
            .order_by(Produto.nome)
        ).all()
    )
    return renderizar(
        request,
        "admin/produtos.html",
        produtos=produtos,
        lixeira=bool(lixeira),
    )


@router.get("/produtos/novo")
def novo_produto_get(request: Request, banco: Sessao) -> Response:
    return renderizar(
        request,
        "admin/produto_form.html",
        produto=None,
        categorias=list(banco.scalars(select(Categoria).order_by(Categoria.nome)).all()),
        valores={},
    )


@router.post("/produtos/novo")
async def novo_produto_post(
    request: Request,
    banco: Sessao,
    nome: Annotated[str, Form()] = "",
    categoria_id: Annotated[int, Form()] = 0,
    descricao: Annotated[str, Form()] = "",
    alergenicos: Annotated[str, Form()] = "",
    preco: Annotated[str, Form()] = "",
    estoque: Annotated[str, Form()] = "",
    ativo: Annotated[str, Form()] = "",
    imagem: Annotated[UploadFile | None, File()] = None,
) -> Response:
    valores = {
        "nome": nome,
        "categoria_id": categoria_id,
        "descricao": descricao,
        "alergenicos": alergenicos,
        "preco": preco,
        "estoque": estoque,
        "ativo": ativo,
    }
    categorias = list(banco.scalars(select(Categoria).order_by(Categoria.nome)).all())
    try:
        nome_limpo, categoria, descricao_limpa, alergenicos_limpos, preco_dec, estoque_int, slug = (
            _validar_produto(
                banco,
                nome=nome,
                categoria_id=categoria_id,
                descricao=descricao,
                alergenicos=alergenicos,
                preco=preco,
                estoque=estoque,
            )
        )
    except ErroAplicacao as erro:
        return renderizar_form(
            request,
            "admin/produto_form.html",
            erro=erro,
            produto=None,
            categorias=categorias,
            valores=valores,
        )
    caminho_imagem = midia.IMAGEM_PADRAO
    if imagem is not None and imagem.filename:
        try:
            caminho_imagem = await midia.salvar_imagem(imagem, slug)
        except ErroAplicacao as erro:
            return renderizar_form(
                request,
                "admin/produto_form.html",
                erro=erro,
                produto=None,
                categorias=categorias,
                valores=valores,
            )
    banco.add(
        Produto(
            categoria_id=categoria.id,
            nome=nome_limpo,
            slug=slug,
            imagem=caminho_imagem,
            descricao=descricao_limpa,
            alergenicos=alergenicos_limpos,
            preco=preco_dec,
            estoque=estoque_int,
            ativo=ativo == "on",
        )
    )
    banco.commit()
    avisar(request, "Produto criado.")
    return redirecionar("/admin/produtos")


@router.get("/produtos/{produto_id}/editar")
def editar_produto_get(request: Request, banco: Sessao, produto_id: int) -> Response:
    produto = _produto(banco, produto_id)
    return renderizar(
        request,
        "admin/produto_form.html",
        produto=produto,
        categorias=list(banco.scalars(select(Categoria).order_by(Categoria.nome)).all()),
        valores={
            "nome": produto.nome,
            "categoria_id": produto.categoria_id,
            "descricao": produto.descricao,
            "alergenicos": produto.alergenicos,
            "preco": f"{produto.preco:.2f}",
            "estoque": str(produto.estoque),
            "ativo": "on" if produto.ativo else "",
        },
    )


@router.post("/produtos/{produto_id}/editar")
async def editar_produto_post(
    request: Request,
    banco: Sessao,
    produto_id: int,
    nome: Annotated[str, Form()] = "",
    categoria_id: Annotated[int, Form()] = 0,
    descricao: Annotated[str, Form()] = "",
    alergenicos: Annotated[str, Form()] = "",
    preco: Annotated[str, Form()] = "",
    estoque: Annotated[str, Form()] = "",
    ativo: Annotated[str, Form()] = "",
    imagem: Annotated[UploadFile | None, File()] = None,
    remover_imagem: Annotated[str, Form()] = "",
) -> Response:
    produto = _produto(banco, produto_id)
    valores = {
        "nome": nome,
        "categoria_id": categoria_id,
        "descricao": descricao,
        "alergenicos": alergenicos,
        "preco": preco,
        "estoque": estoque,
        "ativo": ativo,
    }
    categorias = list(banco.scalars(select(Categoria).order_by(Categoria.nome)).all())
    try:
        nome_limpo, categoria, descricao_limpa, alergenicos_limpos, preco_dec, estoque_int, slug = (
            _validar_produto(
                banco,
                nome=nome,
                categoria_id=categoria_id,
                descricao=descricao,
                alergenicos=alergenicos,
                preco=preco,
                estoque=estoque,
                produto_id=produto.id,
            )
        )
    except ErroAplicacao as erro:
        return renderizar_form(
            request,
            "admin/produto_form.html",
            erro=erro,
            produto=produto,
            categorias=categorias,
            valores=valores,
        )
    nova_imagem = produto.imagem
    if remover_imagem == "on":
        midia.remover_imagem(produto.imagem)
        nova_imagem = midia.IMAGEM_PADRAO
    elif imagem is not None and imagem.filename:
        try:
            nova_imagem = await midia.salvar_imagem(imagem, slug)
        except ErroAplicacao as erro:
            return renderizar_form(
                request,
                "admin/produto_form.html",
                erro=erro,
                produto=produto,
                categorias=categorias,
                valores=valores,
            )
        midia.remover_imagem(produto.imagem)
    produto.categoria_id = categoria.id
    produto.nome = nome_limpo
    produto.slug = slug
    produto.imagem = nova_imagem
    produto.descricao = descricao_limpa
    produto.alergenicos = alergenicos_limpos
    produto.preco = preco_dec
    produto.estoque = estoque_int
    produto.ativo = ativo == "on"
    banco.commit()
    avisar(request, "Produto atualizado.")
    return redirecionar("/admin/produtos")


@router.post("/produtos/{produto_id}/ativo")
def alternar_produto(banco: Sessao, produto_id: int) -> Response:
    produto = _produto(banco, produto_id)
    produto.ativo = not produto.ativo
    banco.commit()
    return redirecionar("/admin/produtos")


@router.post("/produtos/{produto_id}/excluir")
def excluir_produto(request: Request, banco: Sessao, produto_id: int) -> Response:
    produto = _produto(banco, produto_id)
    if produto.excluido_em is not None:
        avisar(request, "Este produto já está na lixeira.", tipo="info")
        return redirecionar("/admin/produtos?lixeira=1")
    produto.ativo = False
    produto.excluido_em = datetime.now(UTC).replace(tzinfo=None)
    banco.commit()
    avisar(request, "Produto movido para a lixeira. Você pode restaurá-lo depois.", tipo="info")
    return redirecionar("/admin/produtos")


@router.post("/produtos/{produto_id}/restaurar")
def restaurar_produto(request: Request, banco: Sessao, produto_id: int) -> Response:
    produto = _produto(banco, produto_id)
    if produto.excluido_em is None:
        avisar(request, "Este produto não está na lixeira.", tipo="info")
        return redirecionar("/admin/produtos")
    produto.excluido_em = None
    produto.ativo = produto.estoque > 0
    banco.commit()
    avisar(request, "Produto restaurado. Revise os dados e ative quando quiser.")
    return redirecionar("/admin/produtos?lixeira=1")


# ---------------------------------------------------------------- categorias
@router.get("/categorias")
def listar_categorias(request: Request, banco: Sessao) -> Response:
    linhas = banco.execute(
        select(Categoria, func.count(Produto.id))
        .outerjoin(Produto, Produto.categoria_id == Categoria.id)
        .group_by(Categoria.id)
        .order_by(Categoria.nome)
    ).all()
    return renderizar(request, "admin/categorias.html", linhas=linhas)


def _categoria_por_nome(
    banco: Session,
    nome: str,
    exceto_id: int | None = None,
) -> Categoria | None:
    consulta = select(Categoria).where(func.lower(Categoria.nome) == nome.lower())
    if exceto_id is not None:
        consulta = consulta.where(Categoria.id != exceto_id)
    return banco.scalar(consulta)


@router.post("/categorias")
def criar_categoria(
    request: Request,
    banco: Sessao,
    nome: Annotated[str, Form()] = "",
) -> Response:
    nome_limpo = texto(nome, minimo=2, maximo=80)
    if nome_limpo is None or _categoria_por_nome(banco, nome_limpo) is not None:
        avisar_codigo(request, "ERR-ADM-001")
        return redirecionar("/admin/categorias")
    banco.add(Categoria(nome=nome_limpo, slug=gerar_slug(nome_limpo), ativo=True))
    try:
        banco.commit()
    except IntegrityError:
        banco.rollback()
        avisar_codigo(request, "ERR-ADM-001")
        return redirecionar("/admin/categorias")
    avisar(request, "Categoria criada.")
    return redirecionar("/admin/categorias")


@router.post("/categorias/{categoria_id}/editar")
def editar_categoria(
    request: Request,
    banco: Sessao,
    categoria_id: int,
    nome: Annotated[str, Form()] = "",
) -> Response:
    categoria = banco.get(Categoria, categoria_id)
    if categoria is None:
        raise ErroAplicacao("ERR-ADM-009")
    nome_limpo = texto(nome, minimo=2, maximo=80)
    if nome_limpo is None or _categoria_por_nome(banco, nome_limpo, categoria.id) is not None:
        avisar_codigo(request, "ERR-ADM-001")
        return redirecionar("/admin/categorias")
    categoria.nome = nome_limpo
    categoria.slug = gerar_slug(nome_limpo)
    try:
        banco.commit()
    except IntegrityError:
        banco.rollback()
        avisar_codigo(request, "ERR-ADM-001")
        return redirecionar("/admin/categorias")
    avisar(request, "Categoria atualizada.")
    return redirecionar("/admin/categorias")


@router.post("/categorias/{categoria_id}/ativo")
def alternar_categoria(banco: Sessao, categoria_id: int) -> Response:
    categoria = banco.get(Categoria, categoria_id)
    if categoria is None:
        raise ErroAplicacao("ERR-ADM-009")
    categoria.ativo = not categoria.ativo
    banco.commit()
    return redirecionar("/admin/categorias")


@router.post("/categorias/{categoria_id}/excluir")
def excluir_categoria(request: Request, banco: Sessao, categoria_id: int) -> Response:
    categoria = banco.get(Categoria, categoria_id)
    if categoria is None:
        raise ErroAplicacao("ERR-ADM-009")
    total = (
        banco.scalar(
            select(func.count()).select_from(Produto).where(Produto.categoria_id == categoria.id)
        )
        or 0
    )
    if total > 0:
        avisar_codigo(request, "ERR-ADM-002")
        return redirecionar("/admin/categorias")
    banco.delete(categoria)
    try:
        banco.commit()
    except IntegrityError:
        banco.rollback()
        avisar_codigo(request, "ERR-ADM-002")
        return redirecionar("/admin/categorias")
    avisar(request, "Categoria excluída.", tipo="info")
    return redirecionar("/admin/categorias")


# ------------------------------------------------------------------- pedidos
@router.get("/pedidos")
def listar_pedidos(
    request: Request,
    banco: Sessao,
    status_filtro: Annotated[str, Query(alias="status", max_length=20)] = "",
) -> Response:
    consulta = (
        select(Pedido).options(selectinload(Pedido.cliente)).order_by(Pedido.criado_em.desc())
    )
    if status_filtro:
        consulta = consulta.where(Pedido.status == status_filtro)
    pedidos = list(banco.scalars(consulta).all())
    return renderizar(
        request,
        "admin/pedidos.html",
        pedidos=pedidos,
        status_filtro=status_filtro,
    )


@router.get("/pedidos/{pedido_id}")
def detalhe_pedido_admin(request: Request, banco: Sessao, pedido_id: int) -> Response:
    pedido = banco.scalar(select(Pedido).where(Pedido.id == pedido_id))
    if pedido is None:
        raise ErroAplicacao("ERR-PED-001")
    entregadores = list(
        banco.scalars(
            select(Usuario)
            .where(Usuario.papel == Papel.ENTREGADOR, Usuario.ativo.is_(True))
            .order_by(Usuario.nome)
        ).all()
    )
    return renderizar(
        request,
        "admin/pedido_detalhe.html",
        pedido=pedido,
        entregadores=entregadores,
        transicoes=transicoes_disponiveis(pedido.status),
    )


@router.post("/pedidos/{pedido_id}/status")
def mudar_status(
    request: Request,
    banco: Sessao,
    pedido_id: int,
    usuario: Annotated[Usuario, Depends(exigir_usuario)],
    destino: Annotated[str, Form()] = "",
    entregador_id: Annotated[str, Form()] = "",
    observacao: Annotated[str, Form()] = "",
) -> Response:
    pedido = banco.scalar(select(Pedido).where(Pedido.id == pedido_id).with_for_update())
    if pedido is None:
        raise ErroAplicacao("ERR-PED-001")
    validar_transicao(pedido.status, destino)

    if destino == StatusPedido.EM_PREPARO and not pedido.pago:
        raise ErroAplicacao(
            "ERR-PED-002",
            detalhe="Pagamento pendente: não é possível iniciar o preparo.",
        )
    if destino == StatusPedido.SAIU_ENTREGA:
        try:
            entregador_escolhido = int(entregador_id)
        except ValueError:
            raise ErroAplicacao(
                "ERR-PED-002",
                detalhe="Selecione um entregador ativo.",
            ) from None
        entregador = banco.scalar(
            select(Usuario).where(
                Usuario.id == entregador_escolhido,
                Usuario.papel == Papel.ENTREGADOR,
                Usuario.ativo.is_(True),
            )
        )
        if entregador is None:
            raise ErroAplicacao(
                "ERR-PED-002",
                detalhe="Selecione um entregador ativo.",
            )
        pedido.entregador_id = entregador.id

    observacao_limpa = observacao.strip()[:255] or None
    if destino == StatusPedido.CANCELADO:
        cancelar_pedido(
            banco,
            pedido,
            usuario.id,
            observacao_limpa or "Cancelado pelo administrador.",
        )
    else:
        pedido.status = destino
        registrar_historico(banco, pedido.id, destino, usuario.id, observacao_limpa)
    banco.commit()
    avisar(request, "Status atualizado.")
    return redirecionar(f"/admin/pedidos/{pedido.id}")


# ----------------------------------------------------------------- relatório
def _data(valor: str, padrao: date) -> date:
    try:
        return date.fromisoformat(valor)
    except ValueError:
        return padrao


@router.get("/relatorio")
def relatorio(
    request: Request,
    banco: Sessao,
    inicio: Annotated[str, Query(max_length=10)] = "",
    fim: Annotated[str, Query(max_length=10)] = "",
) -> Response:
    hoje = datetime.now(ZoneInfo("America/Sao_Paulo")).date()
    data_inicio = _data(inicio, hoje)
    data_fim = _data(fim, hoje)
    if data_inicio > data_fim:
        data_inicio, data_fim = data_fim, data_inicio
    fuso = ZoneInfo("America/Sao_Paulo")
    inicio_dt = (
        datetime.combine(data_inicio, time.min, tzinfo=fuso)
        .astimezone(ZoneInfo("UTC"))
        .replace(tzinfo=None)
    )
    fim_dt = (
        datetime.combine(data_fim, time.max, tzinfo=fuso)
        .astimezone(ZoneInfo("UTC"))
        .replace(tzinfo=None)
    )

    filtro = (
        Pagamento.status == StatusPagamento.APROVADO,
        Pedido.status != StatusPedido.CANCELADO,
        Pedido.criado_em >= inicio_dt,
        Pedido.criado_em <= fim_dt,
    )
    resumo = banco.execute(
        select(
            func.count(Pagamento.id),
            func.coalesce(func.sum(Pagamento.valor), 0),
            func.coalesce(func.avg(Pagamento.valor), 0),
        )
        .join(Pedido, Pedido.id == Pagamento.pedido_id)
        .where(*filtro)
    ).one()
    top_produtos = banco.execute(
        select(ItemPedido.nome_produto, func.sum(ItemPedido.quantidade))
        .join(Pedido, Pedido.id == ItemPedido.pedido_id)
        .join(Pagamento, Pagamento.pedido_id == Pedido.id)
        .where(*filtro)
        .group_by(ItemPedido.nome_produto)
        .order_by(func.sum(ItemPedido.quantidade).desc())
        .limit(5)
    ).all()
    return renderizar(
        request,
        "admin/relatorio.html",
        inicio=data_inicio.isoformat(),
        fim=data_fim.isoformat(),
        pedidos=int(resumo[0] or 0),
        receita=Decimal(resumo[1] or 0),
        ticket=Decimal(resumo[2] or 0),
        top_produtos=top_produtos,
    )


# ------------------------------------------------------------------ usuários
@router.get("/usuarios")
def listar_usuarios(request: Request, banco: Sessao) -> Response:
    usuarios = list(banco.scalars(select(Usuario).order_by(Usuario.nome)).all())
    return renderizar(request, "admin/usuarios.html", usuarios=usuarios)


@router.post("/usuarios/{usuario_id}/papel")
def alterar_papel(
    request: Request,
    banco: Sessao,
    usuario_id: int,
    usuario: Annotated[Usuario, Depends(exigir_usuario)],
    papel: Annotated[str, Form()] = "",
) -> Response:
    alvo = banco.get(Usuario, usuario_id)
    if alvo is None:
        raise ErroAplicacao("ERR-ADM-006")
    if alvo.id == usuario.id:
        raise ErroAplicacao("ERR-ADM-005")
    if papel not in {Papel.CLIENTE, Papel.ENTREGADOR}:
        raise ErroAplicacao("ERR-VAL-001", campos={"papel": "Papel inválido."})
    if alvo.eh_admin:
        admins = (
            banco.scalar(
                select(func.count())
                .select_from(Usuario)
                .where(Usuario.papel == Papel.ADMIN, Usuario.ativo.is_(True))
            )
            or 0
        )
        if admins <= 1:
            raise ErroAplicacao("ERR-ADM-005")
    alvo.papel = papel
    banco.commit()
    avisar(request, "Papel atualizado.")
    return redirecionar("/admin/usuarios")


@router.post("/usuarios/{usuario_id}/ativo")
def alternar_usuario(
    request: Request,
    banco: Sessao,
    usuario_id: int,
    usuario: Annotated[Usuario, Depends(exigir_usuario)],
) -> Response:
    alvo = banco.get(Usuario, usuario_id)
    if alvo is None:
        raise ErroAplicacao("ERR-ADM-006")
    if alvo.id == usuario.id:
        raise ErroAplicacao("ERR-ADM-005")
    if alvo.eh_admin and alvo.ativo:
        admins = (
            banco.scalar(
                select(func.count())
                .select_from(Usuario)
                .where(Usuario.papel == Papel.ADMIN, Usuario.ativo.is_(True))
            )
            or 0
        )
        if admins <= 1:
            raise ErroAplicacao("ERR-ADM-005")
    alvo.ativo = not alvo.ativo
    banco.commit()
    avisar(request, "Situação da conta atualizada.", tipo="info")
    return redirecionar("/admin/usuarios")
