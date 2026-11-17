"""Armazenamento local das imagens enviadas pelo administrador."""

from __future__ import annotations

import secrets
from pathlib import Path

from fastapi import UploadFile

from app.core.config import settings
from app.core.problemas import ErroAplicacao

PREFIXO = "/midia/"
IMAGEM_PADRAO = "/static/img/produtos/padrao.jpg"
TAMANHO_MAXIMO = 2 * 1024 * 1024
ASSINATURAS: tuple[tuple[bytes, str], ...] = (
    (b"\xff\xd8\xff", ".jpg"),
    (b"\x89PNG\r\n\x1a\n", ".png"),
)


def _extensao(conteudo: bytes) -> str | None:
    for assinatura, extensao in ASSINATURAS:
        if conteudo.startswith(assinatura):
            return extensao
    if len(conteudo) >= 12 and conteudo[:4] == b"RIFF" and conteudo[8:12] == b"WEBP":
        return ".webp"
    return None


async def salvar_imagem(arquivo: UploadFile, slug: str) -> str:
    """Valida o conteúdo real e grava a imagem, devolvendo a URL pública."""
    conteudo = await arquivo.read(TAMANHO_MAXIMO + 1)
    if not conteudo:
        raise ErroAplicacao("ERR-ADM-010", detalhe="Selecione um arquivo de imagem.")
    if len(conteudo) > TAMANHO_MAXIMO:
        raise ErroAplicacao("ERR-ADM-010", detalhe="A imagem deve ter no máximo 2 MB.")
    extensao = _extensao(conteudo)
    if extensao is None:
        raise ErroAplicacao(
            "ERR-ADM-010",
            detalhe="Envie uma imagem JPG, PNG ou WebP.",
        )
    nome = f"{slug[:60]}-{secrets.token_hex(6)}{extensao}"
    diretorio = settings.diretorio_midias
    diretorio.mkdir(parents=True, exist_ok=True)
    (diretorio / nome).write_bytes(conteudo)
    return f"{PREFIXO}{nome}"


def remover_imagem(caminho: str | None) -> None:
    """Apaga um arquivo enviado; imagens do pacote estático nunca são tocadas."""
    if not caminho or not caminho.startswith(PREFIXO):
        return
    nome = Path(caminho.removeprefix(PREFIXO)).name
    if not nome:
        return
    alvo = settings.diretorio_midias / nome
    try:
        alvo.unlink()
    except FileNotFoundError:
        return
