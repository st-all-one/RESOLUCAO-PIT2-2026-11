PY := .venv/bin/python
PIP := .venv/bin/pip
MYSQL := docker compose exec -T mysql mysql -uroot -pcupcake_root

.DEFAULT_GOAL := help
.PHONY: help install db-up db-down db-reset schema seed run test cov lint fmt typecheck front-build audit check

help: ## Lista os alvos disponíveis
	@grep -E '^[a-zA-Z_-]+:.*?## ' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

install: ## Cria venv, instala dependências Python e Node
	python3 -m venv .venv
	$(PIP) install -e ".[dev]"
	npm install

db-up: ## Sobe o MySQL (localhost:3307)
	docker compose up -d --wait mysql

db-down: ## Para o MySQL
	docker compose down

db-reset: ## Recria o schema e recarrega o seed
	$(MYSQL) < db/schema.sql
	$(MYSQL) < db/seed.sql

schema: ## Aplica db/schema.sql
	$(MYSQL) < db/schema.sql

seed: ## Aplica db/seed.sql
	$(MYSQL) < db/seed.sql

run: ## Sobe a aplicação em modo desenvolvimento
	$(PY) -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000

test: ## Roda a suíte de testes
	$(PY) -m pytest

cov: ## Roda testes com cobertura
	$(PY) -m pytest --cov=app --cov-report=term-missing --cov-report=xml

lint: ## Lint de back-end e front-end
	$(PY) -m ruff check .
	$(PY) -m ruff format --check .
	npm run lint

typecheck: ## Checagem de tipos (mypy strict + tsc strict)
	$(PY) -m mypy src tests scripts
	npx tsc -p tsconfig.json --noEmit

front-build: ## Compila TypeScript para src/static/js
	npm run build

audit: ## Auditoria de UI com sniff (requer app rodando em :8000)
	mkdir -p artifacts
	sniff capture http://127.0.0.1:8000/ -s "body" --no-summary > artifacts/sniff-home.jsonl
	sniff check artifacts/sniff-home.jsonl

check: lint typecheck test ## Pipeline completo local
