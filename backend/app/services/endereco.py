"""Validação e normalização do endereço de entrega."""

from __future__ import annotations

from dataclasses import dataclass

from app.core.problemas import ErroAplicacao
from app.services.validacao import normalizar_cep, normalizar_uf, texto


@dataclass(frozen=True, slots=True)
class EnderecoValidado:
    cep: str
    logradouro: str
    numero: str
    complemento: str | None
    bairro: str
    cidade: str
    uf: str


def validar_endereco(
    *,
    cep: str,
    logradouro: str,
    numero: str,
    complemento: str,
    bairro: str,
    cidade: str,
    uf: str,
) -> EnderecoValidado:
    cep_limpo = normalizar_cep(cep)
    if cep_limpo is None:
        raise ErroAplicacao("ERR-CHK-002", campos={"cep": "Informe 8 dígitos."})
    uf_limpa = normalizar_uf(uf)
    if uf_limpa is None:
        raise ErroAplicacao("ERR-CHK-003", campos={"uf": "Informe a UF com 2 letras."})
    logradouro_limpo = texto(logradouro, maximo=160)
    numero_limpo = texto(numero, maximo=20)
    bairro_limpo = texto(bairro, maximo=80)
    cidade_limpa = texto(cidade, maximo=80)
    if (
        logradouro_limpo is None
        or numero_limpo is None
        or bairro_limpo is None
        or cidade_limpa is None
    ):
        faltando = {
            nome: "Campo obrigatório."
            for nome, valor in (
                ("logradouro", logradouro_limpo),
                ("numero", numero_limpo),
                ("bairro", bairro_limpo),
                ("cidade", cidade_limpa),
            )
            if valor is None
        }
        raise ErroAplicacao("ERR-CHK-001", campos=faltando)
    complemento_limpo = complemento.strip() or None
    if complemento_limpo is not None and len(complemento_limpo) > 80:
        raise ErroAplicacao(
            "ERR-CHK-001",
            campos={"complemento": "Máximo de 80 caracteres."},
        )
    return EnderecoValidado(
        cep=cep_limpo,
        logradouro=logradouro_limpo,
        numero=numero_limpo,
        complemento=complemento_limpo,
        bairro=bairro_limpo,
        cidade=cidade_limpa,
        uf=uf_limpa,
    )
