PY := .venv/bin/python
PIP := .venv/bin/pip
DB := docker compose exec -T mariadb mariadb -uroot -pcupcake_root cupcake

.DEFAULT_GOAL := help
.PHONY: help install db-up db-down db-reset schema seed run up down logs ps deploy-check test cov lint fmt typecheck front-build audit check

help: ## Lista os alvos disponíveis
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

install: ## Cria venv, instala dependências Python e Node
	python3 -m venv .venv
	$(PIP) install -e ".[dev]"
	npm --prefix frontend install

db-up: ## Sobe o MariaDB (localhost:3307)
	docker compose up -d --wait mariadb

db-down: ## Para o MariaDB
	docker compose down mariadb

db-reset: ## Recria o schema e recarrega o seed
	$(DB) < database/schema.sql
	$(DB) < database/seed.sql

schema: ## Aplica database/schema.sql
	$(DB) < database/schema.sql

seed: ## Aplica database/seed.sql
	$(DB) < database/seed.sql

dicionario: ## Regenera docs/05-dados/dicionario.md a partir do banco
	$(PY) backend/scripts/gerar_dicionario.py

run: ## Sobe a aplicação em modo desenvolvimento
	$(PY) -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

up: ## Sobe banco e aplicação em containers (VPS)
	docker compose up -d --build

down: ## Para aplicação e banco
	docker compose down

logs: ## Acompanha os logs da aplicação
	docker compose logs -f app

ps: ## Mostra o estado dos containers
	docker compose ps

deploy-check: ## Valida um deploy (URL=https://...)
	$(PY) backend/scripts/verificar_deploy.py "$(URL)"

test: ## Roda a suíte de testes
	$(PY) -m pytest

cov: ## Roda testes com cobertura
	$(PY) -m pytest --cov=app --cov-report=term-missing --cov-report=xml

lint: ## Lint de back-end e front-end
	$(PY) -m ruff check .
	$(PY) -m ruff format --check .
	npm --prefix frontend run lint

typecheck: ## Checagem de tipos (mypy strict + tsc strict)
	$(PY) -m mypy backend/app tests backend/scripts
	npm --prefix frontend run typecheck

front-build: ## Compila TypeScript e copia o CSS para backend/app/static
	npm --prefix frontend run build

audit: ## Auditoria de UI com sniff (requer app rodando em :8000)
	mkdir -p artifacts
	sniff capture http://127.0.0.1:8000/ -s "body" --depth 8 > artifacts/sniff-home.jsonl
	sniff capture http://127.0.0.1:8000/cadastro -s "body" --depth 8 > artifacts/sniff-cadastro.jsonl
	sniff check artifacts/sniff-home.jsonl
	sniff check artifacts/sniff-cadastro.jsonl

check: lint typecheck test ## Pipeline completo local
