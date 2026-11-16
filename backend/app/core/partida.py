"""Verificações de partida da aplicação."""

from __future__ import annotations

from sqlalchemy import select

from app.core.config import settings
from app.core.db import SessionLocal
from app.models import Usuario
from app.services.seguranca import verificar_senha

SENHA_DEMONSTRACAO = "Admin@123"


def validar_admin_inicial() -> None:
    """Recusa produção com a senha de demonstração publicada no seed."""
    if settings.app_env != "production":
        return
    with SessionLocal() as banco:
        admin = banco.scalar(select(Usuario).where(Usuario.papel == "admin").limit(1))
        if admin is not None and verificar_senha(SENHA_DEMONSTRACAO, admin.senha_hash):
            raise RuntimeError(
                "O administrador ainda usa a senha de demonstração. "
                "Defina ADMIN_SENHA e rode `make admin-senha` antes de subir."
            )
