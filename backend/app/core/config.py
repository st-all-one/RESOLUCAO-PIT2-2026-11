"""Configuração da aplicação, carregada de variáveis de ambiente e do .env."""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

SEGREDOS_INSEGUROS = frozenset(
    {
        "dev-insecure-change-me",
        "troque-por-uma-chave-aleatoria-de-32-bytes",
    }
)


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
    )

    app_env: str = "development"
    app_secret: str = Field(default="dev-insecure-change-me", min_length=16)
    app_base_url: str = "http://127.0.0.1:8000"

    database_url: str = "mariadb+pymysql://cupcake:cupcake@127.0.0.1:3307/cupcake?charset=utf8mb4"

    session_cookie_secure: bool = False
    session_max_age: int = 86400

    frete_valor: Decimal = Decimal("8.00")
    frete_gratis_acima: Decimal = Decimal("120.00")

    # Imagens enviadas pelo admin; em produção o compose monta um volume aqui.
    diretorio_midias: Path = Path("uploads")

    @model_validator(mode="after")
    def _exigir_producao_segura(self) -> Settings:
        if self.app_env != "production":
            return self
        if len(self.app_secret) < 32 or self.app_secret in SEGREDOS_INSEGUROS:
            raise ValueError("APP_SECRET fraco: em produção use ao menos 32 caracteres aleatórios.")
        if not (self.session_cookie_secure or self.app_base_url.startswith("https://")):
            raise ValueError(
                "Publique atrás de HTTPS e use SESSION_COOKIE_SECURE=true ou "
                "APP_BASE_URL=https://... em produção."
            )
        return self


settings = Settings()
