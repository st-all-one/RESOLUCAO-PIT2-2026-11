"""Engine e sessão SQLAlchemy (MariaDB via PyMySQL)."""

from __future__ import annotations

from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    pool_recycle=3600,
)

SessionLocal = sessionmaker(
    bind=engine,
    class_=Session,
    autoflush=False,
    expire_on_commit=False,
)


def obter_sessao() -> Iterator[Session]:
    """Dependência do FastAPI: uma sessão por requisição."""
    with SessionLocal() as sessao:
        yield sessao
