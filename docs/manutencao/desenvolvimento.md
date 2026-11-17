# Guia de desenvolvimento

## Preparação

```bash
cp .env.example .env
make install        # venv + dependências Python + npm --prefix frontend install
make db-up          # MariaDB em 127.0.0.1:3307
make db-reset       # schema + seed
make front-build    # compila TS e copia o CSS
make run            # http://127.0.0.1:8000
```

`make install` instala o pacote em modo editável apontando para `backend/`.
Depois de mover arquivos ou alterar `pyproject.toml`, repita
`.venv/bin/pip install -e ".[dev]"`.

## Comandos

| Comando | Efeito |
|---|---|
| `make check` | lint + typecheck + testes |
| `make test` / `make cov` | pytest / cobertura |
| `make lint` | ruff + ESLint + Stylelint |
| `make typecheck` | mypy strict + tsc |
| `make front-build` | TS + CSS para `backend/app/static` |
| `make db-reset` | recria o banco de desenvolvimento |
| `make dicionario` | regenera o dicionário de dados |
| `make up` / `make logs` | stack Docker da VPS |
| `make deploy-check URL=…` | smoke test de um deploy |

## Receitas

### Nova rota

1. Crie/abra o controller em `backend/app/controllers/`.
2. Injete `Sessao`, `Request` e a dependência de acesso adequada.
3. Regra de negócio nova → `backend/app/services/`, não no controller.
4. Registre o router em `criar_app()` (`backend/app/main.py`).
5. Crie o template em `backend/app/templates/<área>/` e inclua
   `componentes/erro_form.html` quando houver formulário.
6. Adicione teste de integração em `tests/`.

### Novo erro de domínio

1. Adicione o código e o status em `backend/app/core/problemas.py`.
2. Use `raise ErroAplicacao("ERR-...")`; para formulário, passe `campos=`.
3. Documente em `docs/04-ihc/mensagens-erro.md`.
4. Teste status, `codigo` e campo.

### Alteração de schema

O projeto não usa ferramenta de migração. O fluxo é:

1. Edite `database/schema.sql` (fonte de verdade do DDL).
2. Ajuste `backend/app/models/dominio.py`.
3. Atualize `database/seed.sql` se necessário.
4. Rode `make db-reset` em desenvolvimento.
5. Em produção, aplique a mudança manualmente (ou a migração em
   `database/migracoes/`) e registre no histórico de revisões; `docker compose
   down -v` apaga dados.
6. Atualize o dicionário: `make dicionario`.
7. Teste os CHECKs e FKs afetados.

### Imagens de produto

- O admin grava em `settings.diretorio_midias` (padrão `uploads/`); o volume
  `cupcake-uploads` guarda os arquivos em produção.
- Formatos aceitos: JPG, PNG e WebP de até 2 MB, validados pela assinatura.
- Não há upload público: só o formulário autenticado de admin chama o serviço.

### Alterar CSS ou TypeScript

1. Edite `frontend/src/estilo.css` ou `frontend/src/app.ts`.
2. `make front-build` (ou `npm --prefix frontend run watch` para TS).
3. Recarregue a página; os arquivos servidos ficam em `backend/app/static`.
4. Rode `make lint` e, se mexeu em layout, `make audit`.

### Nova tela com formulário

- Inclua `{% include "componentes/erro_form.html" %}`.
- Todo `<input>` precisa de `<label for>`.
- Campo de formulário sempre com `name`; CSRF via
  `{{ csrf_token(request) }}`.
- Ações destrutivas com `data-confirmar="texto"`.
- Tabelas dentro de `.tabela-responsiva`.

## Depuração

| Sintoma | Verifique |
|---|---|
| `ModuleNotFoundError: app` | refaça `pip install -e ".[dev]"` |
| CSS/JS 404 | `make front-build`; confira `backend/app/static/{css,js}` |
| Login não persiste | cookie `Secure` exige HTTPS; veja `SESSION_COOKIE_SECURE` |
| 403 em POST | token CSRF ausente ou de outra sessão |
| 409 de estoque | estoque mudou entre carrinho e pagamento |
| Relatório vazio | datas em America/Sao_Paulo convertidas para UTC |
| Testes falham na conexão | MariaDB em 3307 e `cupcake_test` criado |
| Template não atualiza | uvicorn sem `--reload`? reinicie `make run` |
| Upload 422 `ERR-ADM-010` | arquivo maior que 2 MB ou sem assinatura JPG/PNG/WebP | converter/reduzir a imagem |

## Armadilhas conhecidas

- **CSRF rotaciona no login**: peça um token novo depois de autenticar.
- **`criado_em` é UTC**: o relatório converte as bordas do dia de São Paulo.
- **Docker + mount**: não monte arquivos dentro de um diretório já montado como
  `:ro`; o runtime não consegue criar o ponto de montagem.
- **`npm --prefix frontend`**: os scripts rodam com cwd em `frontend/`; caminhos
  relativos nos scripts (`stylelint`, `tsconfig`) partem dali.
- **Pacote instalado**: o Docker e o venv usam o pacote de `backend/`; arquivos
  novos em `backend/app` exigem reinstalação para o build da imagem.
