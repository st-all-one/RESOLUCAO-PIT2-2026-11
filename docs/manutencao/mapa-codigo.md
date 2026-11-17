# Mapa de código

## Raiz

| Caminho | Responsabilidade |
|---|---|
| `Makefile` | atalhos de desenvolvimento, banco, deploy e qualidade |
| `compose.yaml` | MariaDB + aplicação para a VPS |
| `Dockerfile` | build multi-stage (Node compila, Python executa) |
| `pyproject.toml` | dependências, empacotamento (`backend/`), pytest, ruff, mypy |
| `README.md` | porta de entrada da documentação |
| `backend/` | código Python e templates |
| `frontend/` | TypeScript, CSS autoral e ferramentas de front |
| `database/` | DDL, seed e init do banco de teste |
| `tests/` | suíte de integração |
| `docs/` | toda a documentação |

## Backend

| Caminho | Responsabilidade |
|---|---|
| `backend/app/main.py` | app factory, middleware, handlers, `/health`, inclusão dos routers |
| `backend/app/core/config.py` | settings via `.env`; frete, sessão, banco |
| `backend/app/core/db.py` | engine e `SessionLocal` |
| `backend/app/core/contexto.py` | usuário/flash/carrinho por requisição |
| `backend/app/core/csrf.py` | token e validação |
| `backend/app/core/acesso.py` | login obrigatório, papéis, redirect |
| `backend/app/core/problemas.py` | catálogo `ERR-*` e Problem Details |
| `backend/app/core/templating.py` | Jinja, filtros (`brl`, `data_br`) e contexto |
| `backend/app/controllers/` | um arquivo por área: `auth`, `conta`, `catalogo`, `carrinho`, `checkout`, `pagamento`, `pedidos`, `admin`, `entregas`, `comum` |
| `backend/app/services/preco.py` | formatação, soma, frete |
| `backend/app/services/carrinho.py` | carrinho puro sobre `dict` |
| `backend/app/services/carrinho_db.py` | carrega produtos e ajusta carrinho à realidade do banco |
| `backend/app/services/endereco.py` | validação única do endereço (checkout e conta) |
| `backend/app/services/midia.py` | valida e grava imagens enviadas pelo admin |
| `backend/app/services/pagamento.py` | Luhn e simulação PIX/cartão |
| `backend/app/services/pedido.py` | rótulos e transições de status |
| `backend/app/services/operacoes.py` | histórico, estoque, cancelamento |
| `backend/app/services/seguranca.py` | scrypt, política de senha |
| `backend/app/services/slug.py` | slug estável |
| `backend/app/services/validacao.py` | CEP, UF, telefone, texto |
| `backend/app/models/dominio.py` | mapeamento das 8 tabelas |
| `backend/app/templates/` | Jinja por feature (`conta/` inclusive) + `base.html` + componentes + erros |
| `backend/app/static/` | **gerado**: CSS copiado e JS compilado |
| `uploads/` | imagens enviadas em desenvolvimento; `/app/uploads` no container |
| `backend/scripts/gerar_dicionario.py` | gera `docs/05-dados/dicionario.md` |
| `backend/scripts/verificar_deploy.py` | smoke test de uma URL publicada |

## Frontend

| Caminho | Responsabilidade |
|---|---|
| `frontend/src/app.ts` | confirmações, máscaras, CEP, alternância PIX/cartão e endereço salvo |
| `frontend/src/estilo.css` | fonte única dos estilos mobile-first |
| `frontend/scripts/copiar-estaticos.mjs` | copia o CSS para o backend |
| `frontend/package.json` | build, watch, typecheck e lint |
| `frontend/tsconfig.json` | TS estrito; saída em `../backend/app/static/js` |
| `frontend/eslint.config.js` | strict-type-checked |
| `frontend/.stylelintrc.json` | padrão de classes e propriedades |

## Banco

| Caminho | Responsabilidade |
|---|---|
| `database/schema.sql` | DDL completo, CHECKs, FKs, índices |
| `database/seed.sql` | 4 usuários, 12 produtos, 3 pedidos de demonstração |
| `database/init/01-banco-de-teste.sql` | cria `cupcake_test` e concede acesso |

## Testes

| Caminho | Responsabilidade |
|---|---|
| `tests/conftest.py` | recria schema, trunca tabelas, dados controlados, `TestClient` |
| `tests/apoio.py` | login, CSRF, compra, pagamento, consultas SQL |
| `tests/test_compra.py` | fluxo PIX/cartão, estoque, cancelamento, isolamento |
| `tests/test_admin.py` | autorização, CRUD, transições, relatório |
| `tests/test_entregas.py` | visibilidade e confirmação |
| `tests/test_auth.py` | cadastro, login, CSRF |
| `tests/test_carrinho.py` | totais, frete, limites |
| `tests/test_catalogo.py` | vitrine, busca, detalhe |
| `tests/test_conta.py` | dados, senha e endereços do cliente |
| `tests/test_servicos.py` | funções puras |
| `tests/test_saude.py` | health e Problem Details |
