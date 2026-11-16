"""Valida um deploy do Cupcake Gourmet por HTTP.

Uso:
    python scripts/verificar_deploy.py https://cupcake.exemplo.com
    python scripts/verificar_deploy.py URL --email admin@... --senha ...

Sai com código 0 quando todas as verificações passam.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from http.cookiejar import CookieJar

PADRAO_TOKEN = re.compile(r'name="csrf_token" value="([^"]+)"')
PADRAO_SLUG = re.compile(r'href="/produtos/([a-z0-9-]+)"')


@dataclass
class Resposta:
    status: int
    url: str
    corpo: str


class Sessao:
    def __init__(self, base: str) -> None:
        self.base = base.rstrip("/")
        self.abridor = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(CookieJar())
        )

    def get(self, caminho: str) -> Resposta:
        with self.abridor.open(self.base + caminho, timeout=15) as resposta:
            return Resposta(
                resposta.status,
                resposta.geturl(),
                resposta.read().decode("utf-8", "replace"),
            )

    def post(self, caminho: str, dados: dict[str, str]) -> Resposta:
        corpo = urllib.parse.urlencode(dados).encode()
        requisicao = urllib.request.Request(  # noqa: S310 (URL http/https validada)
            self.base + caminho,
            data=corpo,
            method="POST",
        )
        try:
            with self.abridor.open(requisicao, timeout=15) as resposta:
                return Resposta(
                    resposta.status,
                    resposta.geturl(),
                    resposta.read().decode("utf-8", "replace"),
                )
        except urllib.error.HTTPError as erro:
            return Resposta(
                erro.code,
                erro.geturl(),
                erro.read().decode("utf-8", "replace"),
            )


def token(pagina: str) -> str:
    achado = PADRAO_TOKEN.search(pagina)
    if achado is None:
        raise SystemExit("token CSRF ausente na página de login")
    return achado.group(1)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("url", help="URL base do deploy")
    parser.add_argument("--email", default="admin@cupcake.local")
    parser.add_argument("--senha", default="Admin@123")
    argumentos = parser.parse_args()
    if not argumentos.url.startswith(("http://", "https://")):
        raise SystemExit("a URL deve começar com http:// ou https://")

    falhas = 0

    def conferir(nome: str, condicao: bool, detalhe: str = "") -> None:
        nonlocal falhas
        if condicao:
            print(f"[ok]     {nome}")
        else:
            falhas += 1
            print(f"[falhou] {nome} {detalhe}".rstrip())

    sessao = Sessao(argumentos.url)

    try:
        saude = sessao.get("/health")
    except OSError as erro:
        print(f"[falhou] conexão com {argumentos.url}: {erro}")
        return 1

    try:
        dados = json.loads(saude.corpo)
    except json.JSONDecodeError:
        dados = {}
    conferir(
        "GET /health",
        saude.status == 200 and dados.get("status") == "ok" and dados.get("db") == "ok",
        f"status={saude.status} corpo={saude.corpo[:120]}",
    )

    inicio = sessao.get("/")
    conferir(
        "vitrine responde",
        inicio.status == 200 and "Cupcake Gourmet" in inicio.corpo,
        f"status={inicio.status}",
    )
    slugs = PADRAO_SLUG.findall(inicio.corpo)
    conferir("vitrine lista produtos", bool(slugs), "nenhum link de produto encontrado")

    if slugs:
        detalhe = sessao.get(f"/produtos/{slugs[0]}")
        conferir(
            f"detalhe /produtos/{slugs[0]}",
            detalhe.status == 200,
            f"status={detalhe.status}",
        )

    login = sessao.get("/login")
    conferir("login responde", login.status == 200, f"status={login.status}")
    entrada = sessao.post(
        "/login",
        {
            "csrf_token": token(login.corpo),
            "email": argumentos.email,
            "senha": argumentos.senha,
            "next": "/admin",
        },
    )
    conferir(
        "autenticação",
        entrada.status == 200 and "/admin" in entrada.url,
        f"status={entrada.status} url={entrada.url}",
    )

    admin = sessao.get("/admin/produtos")
    conferir(
        "administração autenticada",
        admin.status == 200 and "Produtos" in admin.corpo,
        f"status={admin.status}",
    )

    if falhas:
        print(f"\n{falhas} verificação(ões) falharam.")
        return 1
    print("\nDeploy validado: health, vitrine, detalhe, login e administração.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
