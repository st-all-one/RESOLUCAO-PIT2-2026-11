"""Geração de slugs estáveis a partir de texto livre."""

from __future__ import annotations

import re
import unicodedata

LIMITE = 80


def gerar_slug(texto: str) -> str:
    sem_acento = unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("ascii")
    slug = re.sub(r"[^a-z0-9]+", "-", sem_acento.lower()).strip("-")
    return slug[:LIMITE].strip("-") or "item"
