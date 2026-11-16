"""Modelo de domínio mapeado para o schema MariaDB em db/schema.sql."""

from __future__ import annotations

from datetime import datetime
from decimal import Decimal

from sqlalchemy import BigInteger, Boolean, DateTime, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from app.models.tipos import Papel


class Base(DeclarativeBase):
    pass


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    email: Mapped[str] = mapped_column(String(254), nullable=False, unique=True)
    senha_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    telefone: Mapped[str | None] = mapped_column(String(11), nullable=True)
    papel: Mapped[str] = mapped_column(String(20), nullable=False, default=Papel.CLIENTE)
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    criado_em: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    pedidos: Mapped[list[Pedido]] = relationship(
        back_populates="cliente",
        foreign_keys="Pedido.cliente_id",
    )
    entregas: Mapped[list[Pedido]] = relationship(
        back_populates="entregador",
        foreign_keys="Pedido.entregador_id",
    )

    @property
    def eh_admin(self) -> bool:
        return self.papel == Papel.ADMIN

    @property
    def eh_entregador(self) -> bool:
        return self.papel == Papel.ENTREGADOR


class Categoria(Base):
    __tablename__ = "categorias"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(String(80), nullable=False, unique=True)
    slug: Mapped[str] = mapped_column(String(80), nullable=False, unique=True)
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    criado_em: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    produtos: Mapped[list[Produto]] = relationship(back_populates="categoria")


class Produto(Base):
    __tablename__ = "produtos"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    categoria_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("categorias.id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
    )
    nome: Mapped[str] = mapped_column(String(120), nullable=False)
    slug: Mapped[str] = mapped_column(String(140), nullable=False, unique=True)
    descricao: Mapped[str] = mapped_column(Text, nullable=False)
    alergenicos: Mapped[str] = mapped_column(String(255), nullable=False)
    preco: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    estoque: Mapped[int] = mapped_column(nullable=False, default=0)
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    criado_em: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    categoria: Mapped[Categoria] = relationship(back_populates="produtos")

    @property
    def esgotado(self) -> bool:
        return self.estoque <= 0


class Endereco(Base):
    __tablename__ = "enderecos"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    usuario_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("usuarios.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    cep: Mapped[str] = mapped_column(String(8), nullable=False)
    logradouro: Mapped[str] = mapped_column(String(160), nullable=False)
    numero: Mapped[str] = mapped_column(String(20), nullable=False)
    complemento: Mapped[str | None] = mapped_column(String(80), nullable=True)
    bairro: Mapped[str] = mapped_column(String(80), nullable=False)
    cidade: Mapped[str] = mapped_column(String(80), nullable=False)
    uf: Mapped[str] = mapped_column(String(2), nullable=False)
    principal: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    criado_em: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )


class Pedido(Base):
    __tablename__ = "pedidos"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    cliente_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("usuarios.id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
    )
    entregador_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("usuarios.id", ondelete="SET NULL", onupdate="CASCADE"),
        nullable=True,
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="recebido")
    frete: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False, default=Decimal("0.00"))
    cep: Mapped[str] = mapped_column(String(8), nullable=False)
    logradouro: Mapped[str] = mapped_column(String(160), nullable=False)
    numero: Mapped[str] = mapped_column(String(20), nullable=False)
    complemento: Mapped[str | None] = mapped_column(String(80), nullable=True)
    bairro: Mapped[str] = mapped_column(String(80), nullable=False)
    cidade: Mapped[str] = mapped_column(String(80), nullable=False)
    uf: Mapped[str] = mapped_column(String(2), nullable=False)
    telefone_contato: Mapped[str] = mapped_column(String(11), nullable=False)
    criado_em: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    cliente: Mapped[Usuario] = relationship(
        back_populates="pedidos",
        foreign_keys=[cliente_id],
    )
    entregador: Mapped[Usuario | None] = relationship(
        back_populates="entregas",
        foreign_keys=[entregador_id],
    )
    itens: Mapped[list[ItemPedido]] = relationship(
        back_populates="pedido",
        cascade="all, delete-orphan",
        lazy="selectin",
    )
    pagamento: Mapped[Pagamento | None] = relationship(
        back_populates="pedido",
        uselist=False,
        lazy="selectin",
    )
    historico: Mapped[list[HistoricoPedido]] = relationship(
        back_populates="pedido",
        cascade="all, delete-orphan",
        order_by="HistoricoPedido.criado_em",
    )

    @property
    def subtotal(self) -> Decimal:
        return sum((item.subtotal for item in self.itens), start=Decimal("0.00"))

    @property
    def total(self) -> Decimal:
        return self.subtotal + self.frete

    @property
    def pago(self) -> bool:
        return self.pagamento is not None and self.pagamento.status == "aprovado"


class ItemPedido(Base):
    __tablename__ = "itens_pedido"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    pedido_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("pedidos.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    produto_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("produtos.id", ondelete="RESTRICT", onupdate="CASCADE"),
        nullable=False,
    )
    nome_produto: Mapped[str] = mapped_column(String(120), nullable=False)
    preco_unitario: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    quantidade: Mapped[int] = mapped_column(nullable=False)

    pedido: Mapped[Pedido] = relationship(back_populates="itens")
    produto: Mapped[Produto] = relationship()

    @property
    def subtotal(self) -> Decimal:
        return self.preco_unitario * self.quantidade


class Pagamento(Base):
    __tablename__ = "pagamentos"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    pedido_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("pedidos.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
        unique=True,
    )
    metodo: Mapped[str | None] = mapped_column(String(20), nullable=True)
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pendente")
    valor: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    cartao_ultimos4: Mapped[str | None] = mapped_column(String(4), nullable=True)
    codigo_autorizacao: Mapped[str | None] = mapped_column(String(40), nullable=True)
    criado_em: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )

    pedido: Mapped[Pedido] = relationship(back_populates="pagamento")


class HistoricoPedido(Base):
    __tablename__ = "historico_pedido"

    id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    pedido_id: Mapped[int] = mapped_column(
        BigInteger,
        ForeignKey("pedidos.id", ondelete="CASCADE", onupdate="CASCADE"),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(String(20), nullable=False)
    usuario_id: Mapped[int | None] = mapped_column(
        BigInteger,
        ForeignKey("usuarios.id", ondelete="SET NULL", onupdate="CASCADE"),
        nullable=True,
    )
    observacao: Mapped[str | None] = mapped_column(String(255), nullable=True)
    criado_em: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now()
    )

    pedido: Mapped[Pedido] = relationship(back_populates="historico")
    usuario: Mapped[Usuario | None] = relationship()
