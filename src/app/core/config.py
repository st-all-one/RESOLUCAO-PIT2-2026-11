"""Configuração da aplicação, carregada de variáveis de ambiente e do .env."""

from __future__ import annotations

from decimal import Decimal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


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

    database_url: str = (
        "mariadb+pymysql://cupcake:cupcake@127.0.0.1:3307/cupcake?charset=utf8mb4"
    )
    test_database_url: str | None = None

    session_cookie_secure: bool = False
    session_max_age: int = 86400

    frete_valor: Decimal = Decimal("8.00")
    frete_gratis_acima: Decimal = Decimal("120.00")


settings = Settings()
