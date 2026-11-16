# Cupcake Gourmet — PIT Engenharia de Software II (2026/11)

Solução funcional da loja de cupcakes gourmet planejada no PIT I, revisada e
implementada no PIT II. Aplicação web mobile-first com back-end em Python
(FastAPI, padrão MVC), banco MySQL e front-end em HTML, CSS e TypeScript.

## Stack

| Camada | Tecnologia |
|---|---|
| Back-end | Python 3.13+, FastAPI, SQLAlchemy 2, PyMySQL |
| Arquitetura | MVC (`models/`, `controllers/`, `services/`, `templates/`) |
| Banco | MySQL 8.4, schema versionado em `db/schema.sql` |
| Front-end | Jinja2, CSS, TypeScript estrito compilado por `tsc` |
| Testes | pytest + httpx (ASGI), MySQL real |
| Qualidade | ruff, mypy strict, ESLint strict-type-checked, Stylelint, sniff |
| Deploy | a definir na fase P10 (serviço com MySQL) |

## Como rodar

Pré-requisitos: Python 3.13+, Node 22+, Docker.

```bash
cp .env.example .env
make install      # cria .venv, instala dependências Python e Node
make db-up        # sobe MySQL em 127.0.0.1:3307
make db-reset     # aplica schema + seed
make front-build  # compila TypeScript
make run          # http://127.0.0.1:8000
```

Contas de demonstração (seed): `admin@cupcake.local` / `Admin@123`,
`cliente@cupcake.local` / `Cliente@123`, `entregador@cupcake.local` / `Entrega@123`.

## Qualidade

```bash
make check    # ruff + mypy + eslint + stylelint + pytest
make audit    # sniff contra a aplicação em execução
```

## Estrutura

```text
docs/            documentação por fase (planejamento, especificação, UML, IHC, dados, testes, laudo)
db/              schema.sql e seed.sql
frontend/src/    TypeScript (fonte)
src/app/         aplicação FastAPI (models, controllers, services, templates, static)
tests/           testes automatizados
```

## Documentação

- [Planejamento e revisão do PIT I](docs/01-planejamento/)
- [Especificação ágil](docs/02-especificacao/)
- [UML](docs/03-uml/)
- [IHC](docs/04-ihc/)
- [Projeto de dados](docs/05-dados/)
- [Testes](docs/06-testes/)
- [Laudo de qualidade](docs/07-laudo/)
- [Manual de uso](docs/manual-de-uso.md)

## Entrega

| Item | Valor |
|---|---|
| Repositório | https://github.com/st-all-one/RESOLUCAO-PIT2-2026-11 |
| Solução em funcionamento | _a preencher no deploy_ |
| Vídeo narrado (≥ 5 min) | _a preencher_ |
| Vídeo das correções (≤ 5 min) | _a preencher_ |

Entrega prevista: 2026-11-16.
