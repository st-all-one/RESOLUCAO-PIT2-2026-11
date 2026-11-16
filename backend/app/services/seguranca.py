"""Hash de senha (scrypt) e validações de identidade."""

from __future__ import annotations

import base64
import binascii
import hashlib
import hmac
import re
import secrets

N = 16384
R = 8
P = 1
TAMANHO_HASH = 64
TAMANHO_SALT = 16
FORMATO = "scrypt"
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
HASH_SEM_CONTA = (
    "scrypt$16384$8$1$wHgZqJYMfqyaOIWYD/kf9w==$"
    "XCEU7t7CxrN23u8QE25GOg6bxQ6H3DMRzTi/r84Ks0plZMwRn+7ykKDThkkz6kP6t6b/IKfDECiglcunducZCw=="
)


def _b64(dados: bytes) -> str:
    return base64.b64encode(dados).decode("ascii")


def hash_senha(senha: str) -> str:
    salt = secrets.token_bytes(TAMANHO_SALT)
    derivado = hashlib.scrypt(
        senha.encode("utf-8"),
        salt=salt,
        n=N,
        r=R,
        p=P,
        dklen=TAMANHO_HASH,
    )
    return f"{FORMATO}${N}${R}${P}${_b64(salt)}${_b64(derivado)}"


def verificar_senha(senha: str, armazenado: str) -> bool:
    partes = armazenado.split("$")
    if len(partes) != 6 or partes[0] != FORMATO:
        return False
    try:
        n, r, p = int(partes[1]), int(partes[2]), int(partes[3])
        salt = base64.b64decode(partes[4], validate=True)
        esperado = base64.b64decode(partes[5], validate=True)
    except (ValueError, binascii.Error):
        return False
    try:
        calculado = hashlib.scrypt(
            senha.encode("utf-8"),
            salt=salt,
            n=n,
            r=r,
            p=p,
            dklen=len(esperado),
        )
    except ValueError:
        return False
    return hmac.compare_digest(calculado, esperado)


def normalizar_email(email: str) -> str:
    return email.strip().lower()


def email_valido(email: str) -> bool:
    return len(email) <= 254 and EMAIL_RE.fullmatch(email) is not None


def senha_forte(senha: str) -> bool:
    if len(senha) < 8:
        return False
    tem_letra = any(caractere.isalpha() for caractere in senha)
    tem_numero = any(caractere.isdigit() for caractere in senha)
    return tem_letra and tem_numero
