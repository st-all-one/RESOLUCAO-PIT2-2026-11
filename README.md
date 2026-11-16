# Cupcake Gourmet — PIT Engenharia de Software II (2026/11)

Solução funcional da loja de cupcakes gourmet planejada no PIT I, revisada e
implementada no PIT II. Aplicação web mobile-first com back-end em Python
(FastAPI, padrão MVC), banco MariaDB e front-end em HTML, CSS e TypeScript.

## Stack

| Camada | Tecnologia |
|---|---|
| Back-end | Python 3.13+, FastAPI, SQLAlchemy 2 (dialeto MariaDB), PyMySQL |
| Arquitetura | MVC (`models/`, `controllers/`, `services/`, `templates/`) |
| Banco | MariaDB 11.4, schema versionado em `database/schema.sql` |
| Front-end | Jinja2, CSS, TypeScript estrito compilado por `tsc` |
| Testes | pytest + httpx (ASGI), MariaDB real |
| Qualidade | ruff, mypy strict, ESLint strict-type-checked, Stylelint, sniff |
| Deploy | a definir na fase P10 (serviço com MariaDB) |

## Como rodar

Pré-requisitos: Python 3.13+, Node 22+, Docker.

```bash
cp .env.example .env
make install      # cria .venv, instala dependências Python e Node
make db-up        # sobe MariaDB em 127.0.0.1:3307
make db-reset     # aplica schema + seed
make front-build  # compila TypeScript
make run          # http://127.0.0.1:8000
```

Contas de demonstração (seed): `admin@cupcake.local` / `Admin@123`,
`cliente@cupcake.local` / `Cliente@123`, `entregador@cupcake.local` / `Entrega@123`.
Essas senhas são públicas e servem apenas para desenvolvimento; em produção o
startup recusa a senha do admin do seed até `make admin-senha` ser executado.

## Produção (VPS com Docker)

O `compose.yaml` sobe aplicação + MariaDB; o schema e o seed são aplicados na
primeira inicialização do volume.

Em produção o `compose.yaml` exige `APP_SECRET`, senhas do MariaDB, HTTPS e
`SESSION_COOKIE_SECURE=true`; a aplicação escuta apenas em `127.0.0.1` e deve
ficar atrás de um proxy TLS. O passo a passo, incluindo a troca da senha do
administrador antes da primeira subida, está em `docs/08-deploy/deploy.md`.

Guia completo (HTTPS, backup, atualização e verificação) em
[docs/08-deploy/deploy.md](docs/08-deploy/deploy.md).

## Qualidade

```bash
make check    # ruff + mypy + pytest
make lint     # ruff + ESLint + Stylelint
make typecheck
make cov      # cobertura (relatório em coverage.xml)
make audit    # sniff contra a aplicação em execução
```

Resultado atual: 76 testes aprovados, cobertura de 86%, ruff/mypy/ESLint/Stylelint
sem erros e contraste WCAG AAA aprovado no sniff. Detalhes em
[docs/06-testes/relatorio.md](docs/06-testes/relatorio.md) e
[docs/07-laudo/laudo-qualidade.md](docs/07-laudo/laudo-qualidade.md).

A suíte usa um banco separado (`cupcake_test`), criado automaticamente pelo
script `database/init/01-banco-de-teste.sql` na primeira inicialização do volume.
Não é necessário criar dados: cada teste trunca as tabelas e insere um cenário
próprio.

## Estrutura

```text
backend/         aplicação FastAPI (app/, scripts/) — controllers, services, models e templates
database/        schema.sql, seed.sql e init do banco de teste
frontend/        TypeScript, CSS autoral, tsconfig, ESLint e Stylelint
tests/           suíte pytest de integração (MariaDB real)
docs/            documentação funcional, técnica e de manutenção
artifacts/       capturas do sniff usadas no laudo (gerado)
```

## Documentação

- [Planejamento e revisão do PIT I](docs/01-planejamento/)
- [Especificação ágil](docs/02-especificacao/)
- [Rastreabilidade história → código → teste](docs/02-especificacao/rastreabilidade.md)
- [UML](docs/03-uml/diagramas.md)
- [IHC](docs/04-ihc/)
- [Projeto de dados](docs/05-dados/)
- [Testes](docs/06-testes/relatorio.md)
- [Laudo de qualidade](docs/07-laudo/laudo-qualidade.md)
- [Deploy](docs/08-deploy/deploy.md)
- [Template de laudo dos testadores](docs/07-laudo/template-laudo-testador.md)
- [Manual de uso](docs/manual-de-uso.md)
- [Manutenção: arquitetura, convenções, mapa de código e runbook](docs/manutencao/README.md)

## Entrega

| Item | Valor |
|---|---|
| Repositório | https://github.com/st-all-one/RESOLUCAO-PIT2-2026-11 |
| Solução em funcionamento | _a preencher no deploy_ |
| Vídeo narrado (≥ 5 min) | _a preencher_ |
| Vídeo das correções (≤ 5 min) | _a preencher_ |

Entrega prevista: 2026-11-16.
