"""Templates Jinja2, filtros e contexto padrão."""

from __future__ import annotations

from pathlib import Path

from fastapi import Request
from fastapi.templating import Jinja2Templates

from app.core.csrf import obter_token
from app.services.pedido import ROTULOS_STATUS
from app.services.preco import formatar_brl, formatar_data

DIRETORIO = Path(__file__).resolve().parent.parent / "templates"
templates = Jinja2Templates(directory=str(DIRETORIO))
templates.env.filters["brl"] = formatar_brl
templates.env.filters["data_br"] = formatar_data
templates.env.globals["csrf_token"] = obter_token
templates.env.globals["rotulos_status"] = ROTULOS_STATUS
templates.env.globals["rotulos_campos"] = {
    "nome": "Nome",
    "email": "E-mail",
    "senha": "Senha",
    "confirmacao": "Confirmação de senha",
    "cep": "CEP",
    "logradouro": "Logradouro",
    "numero": "Número",
    "complemento": "Complemento",
    "bairro": "Bairro",
    "cidade": "Cidade",
    "uf": "UF",
    "telefone": "Telefone",
    "numero_cartao": "Número do cartão",
    "categoria_id": "Categoria",
    "preco": "Preço",
    "estoque": "Estoque",
    "entregador_id": "Entregador",
    "papel": "Papel",
}


def contexto(request: Request, **extra: object) -> dict[str, object]:
    """Contexto comum a todas as páginas."""
    base: dict[str, object] = {
        "usuario": getattr(request.state, "usuario", None),
        "flash": getattr(request.state, "flash", []),
        "carrinho_quantidade": getattr(request.state, "carrinho_quantidade", 0),
        "request_id": getattr(request.state, "request_id", ""),
    }
    base.update(extra)
    return base
