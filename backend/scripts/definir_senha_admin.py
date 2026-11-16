"""Define a senha de um administrador a partir do ambiente.

Uso:
    ADMIN_SENHA='...' make admin-senha
"""

from __future__ import annotations

import os
import sys

from sqlalchemy import select

from app.core.db import SessionLocal
from app.models import Papel, Usuario
from app.services.seguranca import hash_senha, normalizar_email, senha_forte


def main() -> int:
    email = normalizar_email(os.environ.get("ADMIN_EMAIL", "admin@cupcake.projeto"))
    senha = os.environ.get("ADMIN_SENHA", "")
    if not senha_forte(senha):
        print(
            "ADMIN_SENHA ausente ou fraca: use ao menos 8 caracteres, com letra e número.",
            file=sys.stderr,
        )
        return 1
    with SessionLocal() as banco:
        admin = banco.scalar(select(Usuario).where(Usuario.email == email))
        if admin is None or admin.papel != Papel.ADMIN:
            print(f"Administrador não encontrado: {email}", file=sys.stderr)
            return 1
        admin.senha_hash = hash_senha(senha)
        admin.sessao_versao += 1
        banco.commit()
    print(f"Senha de {email} atualizada.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
