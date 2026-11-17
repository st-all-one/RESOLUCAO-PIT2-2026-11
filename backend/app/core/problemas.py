"""Problem Details (RFC 9457) e o catálogo de erros da aplicação."""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field

from fastapi import Request
from fastapi.responses import JSONResponse


@dataclass(frozen=True, slots=True)
class Definicao:
    status: int
    titulo: str
    detalhe: str


# O código é o contrato estável; o texto pode melhorar sem quebrar testes.
CATALOGO: dict[str, Definicao] = {
    # Autenticação e autorização
    "ERR-AUTH-001": Definicao(401, "Credenciais inválidas", "E-mail ou senha inválidos."),
    "ERR-AUTH-002": Definicao(409, "E-mail já cadastrado", "Este e-mail já está cadastrado."),
    "ERR-AUTH-003": Definicao(
        422,
        "Senha fraca",
        "A senha precisa ter ao menos 8 caracteres, com letra e número.",
    ),
    "ERR-AUTH-004": Definicao(422, "Senhas divergentes", "As senhas não conferem."),
    "ERR-AUTH-005": Definicao(422, "Dados inválidos", "Informe nome e e-mail válidos."),
    "ERR-AUTH-006": Definicao(
        403,
        "Conta desativada",
        "Esta conta está desativada. Procure o administrador.",
    ),
    "ERR-AUTH-007": Definicao(
        403,
        "Acesso negado",
        "Você não tem permissão para acessar esta área.",
    ),
    "ERR-AUTH-008": Definicao(
        403,
        "Sessão inválida",
        "Sua sessão expirou. Entre novamente.",
    ),
    "ERR-AUTH-009": Definicao(
        401,
        "Autenticação necessária",
        "Autenticação necessária.",
    ),
    "ERR-AUTH-010": Definicao(
        429,
        "Muitas tentativas",
        "Muitas tentativas de acesso. Aguarde alguns minutos.",
    ),
    # Catálogo e carrinho
    "ERR-CAT-001": Definicao(404, "Produto não encontrado", "Produto não encontrado."),
    "ERR-CAT-002": Definicao(409, "Produto esgotado", "Este produto está esgotado."),
    "ERR-CAT-003": Definicao(422, "Quantidade inválida", "Informe uma quantidade válida."),
    "ERR-CAR-001": Definicao(409, "Carrinho vazio", "Seu carrinho está vazio."),
    "ERR-CAR-002": Definicao(
        409,
        "Estoque insuficiente",
        "Quantidade acima do estoque disponível.",
    ),
    "ERR-CAR-003": Definicao(
        409,
        "Carrinho ajustado",
        "O carrinho foi atualizado porque um item esgotou.",
    ),
    # Checkout e pagamento
    "ERR-CHK-001": Definicao(
        422,
        "Endereço incompleto",
        "Preencha todos os campos obrigatórios do endereço.",
    ),
    "ERR-CHK-002": Definicao(422, "CEP inválido", "CEP inválido. Informe 8 dígitos."),
    "ERR-CHK-003": Definicao(422, "UF inválida", "UF inválida."),
    "ERR-CHK-004": Definicao(
        503,
        "Consulta de CEP indisponível",
        "Não foi possível consultar o CEP agora. Preencha o endereço manualmente.",
    ),
    "ERR-CHK-005": Definicao(
        404,
        "CEP não encontrado",
        "CEP não encontrado. Confira os 8 dígitos.",
    ),
    "ERR-PAG-001": Definicao(
        402,
        "Pagamento recusado",
        "Pagamento recusado pela operadora simulada.",
    ),
    "ERR-PAG-002": Definicao(422, "Cartão inválido", "Número de cartão inválido."),
    "ERR-PAG-003": Definicao(409, "Pedido já pago", "Este pedido já está pago."),
    "ERR-PAG-004": Definicao(
        409,
        "Estoque insuficiente",
        "Estoque insuficiente para concluir o pagamento.",
    ),
    # Pedidos
    "ERR-PED-001": Definicao(404, "Pedido não encontrado", "Pedido não encontrado."),
    "ERR-PED-002": Definicao(
        409,
        "Transição inválida",
        "Transição de status inválida.",
    ),
    "ERR-PED-003": Definicao(
        409,
        "Cancelamento não permitido",
        "Este pedido não pode mais ser cancelado.",
    ),
    "ERR-PED-004": Definicao(422, "Pedido sem itens", "O pedido não possui itens."),
    # Administração e entrega
    "ERR-ADM-001": Definicao(
        409,
        "Categoria inválida",
        "Informe um nome de categoria único.",
    ),
    "ERR-ADM-002": Definicao(
        409,
        "Categoria em uso",
        "A categoria possui produtos e não pode ser excluída.",
    ),
    "ERR-ADM-003": Definicao(422, "Preço inválido", "O preço deve ser maior que zero."),
    "ERR-ADM-004": Definicao(422, "Estoque inválido", "O estoque não pode ser negativo."),
    "ERR-ADM-005": Definicao(
        409,
        "Operação bloqueada",
        "Você não pode desativar a própria conta.",
    ),
    "ERR-ADM-006": Definicao(404, "Usuário não encontrado", "Usuário não encontrado."),
    "ERR-ADM-008": Definicao(
        409,
        "Produto duplicado",
        "Já existe um produto com esse nome.",
    ),
    "ERR-ADM-009": Definicao(404, "Categoria não encontrada", "Categoria não encontrada."),
    "ERR-ADM-010": Definicao(
        422,
        "Imagem inválida",
        "Envie uma imagem JPG, PNG ou WebP de até 2 MB.",
    ),
    "ERR-END-001": Definicao(
        404,
        "Endereço não encontrado",
        "Endereço não encontrado na sua conta.",
    ),
    "ERR-ENT-001": Definicao(
        403,
        "Entrega não atribuída",
        "Esta entrega não está atribuída a você.",
    ),
    # Sistema
    "ERR-SYS-001": Definicao(
        500,
        "Erro interno",
        "Não foi possível concluir a operação. Tente novamente.",
    ),
    "ERR-SYS-002": Definicao(
        503,
        "Serviço indisponível",
        "Serviço temporariamente indisponível.",
    ),
    "ERR-SYS-003": Definicao(404, "Página não encontrada", "Página não encontrada."),
    "ERR-SYS-004": Definicao(
        405,
        "Método não permitido",
        "Este endereço não aceita o método usado.",
    ),
    "ERR-VAL-001": Definicao(
        422,
        "Dados inválidos",
        "Dados inválidos. Confira os campos destacados.",
    ),
}


class ErroAplicacao(Exception):
    """Única exceção de domínio: carrega um código do catálogo."""

    codigo: str
    status: int
    titulo: str
    detalhe: str
    campos: dict[str, str]

    def __init__(
        self,
        codigo: str,
        *,
        campos: Mapping[str, str] | None = None,
        detalhe: str | None = None,
    ) -> None:
        definicao = CATALOGO.get(codigo)
        if definicao is None:
            raise KeyError(f"Código de problema desconhecido: {codigo}")
        self.codigo = codigo
        self.status = definicao.status
        self.titulo = definicao.titulo
        self.detalhe = detalhe or definicao.detalhe
        self.campos = dict(campos or {})
        super().__init__(f"{codigo}: {self.detalhe}")


@dataclass(frozen=True, slots=True)
class Problema:
    """Representação RFC 9457 de uma falha."""

    codigo: str
    status: int
    titulo: str
    detalhe: str
    instance: str
    campos: dict[str, str] = field(default_factory=dict)

    def para_dict(self) -> dict[str, object]:
        corpo: dict[str, object] = {
            "type": f"https://cupcake-gourmet.local/problemas/{self.codigo.lower()}",
            "title": self.titulo,
            "status": self.status,
            "detail": self.detalhe,
            "instance": self.instance,
            "codigo": self.codigo,
        }
        if self.campos:
            corpo["campos"] = dict(self.campos)
        return corpo

    @classmethod
    def de_erro(cls, erro: ErroAplicacao, instance: str) -> Problema:
        return cls(
            codigo=erro.codigo,
            status=erro.status,
            titulo=erro.titulo,
            detalhe=erro.detalhe,
            instance=instance,
            campos=dict(erro.campos),
        )

    @classmethod
    def generico(
        cls,
        *,
        codigo: str,
        status: int,
        instance: str,
        detalhe: str | None = None,
        campos: Mapping[str, str] | None = None,
    ) -> Problema:
        definicao = CATALOGO[codigo]
        return cls(
            codigo=codigo,
            status=status,
            titulo=definicao.titulo,
            detalhe=detalhe or definicao.detalhe,
            instance=instance,
            campos=dict(campos or {}),
        )


def prefere_json(request: Request) -> bool:
    """Negociação de conteúdo: API e /health sempre em JSON."""
    caminho = request.url.path
    if caminho == "/health" or caminho.startswith("/api"):
        return True
    aceite = request.headers.get("accept", "")
    return "application/problem+json" in aceite or "application/json" in aceite


def resposta_json(
    problema: Problema,
    *,
    headers: dict[str, str] | None = None,
) -> JSONResponse:
    return JSONResponse(
        content=problema.para_dict(),
        status_code=problema.status,
        media_type="application/problem+json",
        headers=headers,
    )
