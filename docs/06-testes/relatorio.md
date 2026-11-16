# Relatório de testes automatizados

## Estratégia

A suíte é de **integração**, executada contra um MariaDB real (`cupcake_test`),
porque as regras críticas dependem de transações, `CHECK`, chaves únicas e
baixa condicional de estoque — comportamentos que mocks não reproduzem.

- Sessão única: o schema é recriado a partir de `database/schema.sql`.
- Isolamento por teste: todas as tabelas são truncadas antes de cada caso.
- Dados controlados: 5 usuários, 2 categorias e 5 produtos (um inativo, um de
  frete grátis, estoques pequenos para forçar limite).
- Cliente HTTP: `TestClient` (ASGI) com cookie de sessão e CSRF reais.

## Como executar

```bash
make db-up          # MariaDB em 127.0.0.1:3307
make test           # pytest
make cov            # cobertura com relatório XML
```

O banco `cupcake_test` é criado pelo script `database/init/01-banco-de-teste.sql`
na primeira inicialização do volume. Em um banco já existente:

```sql
CREATE DATABASE IF NOT EXISTS cupcake_test
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
GRANT ALL PRIVILEGES ON cupcake_test.* TO 'cupcake'@'%';
```

## Resultado (2026-11-16)

- **76 testes, 76 aprovados** em ~30 s.
- **Cobertura de linhas: 86%** (`backend/app`, 1557 linhas, 212 sem cobertura).
- Falha rápida em regressões de preço, frete, CSRF, estoque e autorização.

Cobertura por módulo (principais):

| Módulo | Cobertura |
|---|---|
| `services/pagamento.py` | 100% |
| `services/pedido.py` | 100% |
| `services/validacao.py` | 100% |
| `services/slug.py` | 100% |
| `services/identificador.py` | 100% |
| `core/db.py`, `core/templating.py` | 100% |
| `controllers/auth.py` | 91% |
| `controllers/checkout.py` | 82% |
| `controllers/pagamento.py` | 90% |
| `controllers/admin.py` | 61% |
| `main.py` | 79% |

`controllers/admin.py` concentra muitos ramos de erro (exclusões protegidas,
validações de formulário); os fluxos principais estão cobertos e os ramos
restantes são exercitados manualmente no roteiro do laudo.

## Casos cobertos

| Arquivo | Foco |
|---|---|
| `test_saude.py` | health check e Problem Details |
| `test_catalogo.py` | vitrine, busca, categoria, detalhe, 404 JSON |
| `test_auth.py` | cadastro, hash, login/logout, conta inativa, CSRF |
| `test_carrinho.py` | totais, frete grátis, limite de estoque, atualização e remoção |
| `test_compra.py` | PIX, cartão inválido, recusa final 0000, estoque esgotado, cancelamento, isolamento, CEP, itens no checkout, código público |
| `test_admin.py` | autorização, CRUD, transições, relatório, autoproteção do admin |
| `test_entregas.py` | lista, confirmação e isolamento entre entregadores |
| `test_servicos.py` | dinheiro, frete, Luhn, slug, validação, senha, máquina de estados |

## Limitações conhecidas

- A suíte exige o MariaDB do `compose.yaml` em execução; não há modo SQLite.
- Não há teste de navegador (E2E): a camada visual é verificada por `sniff` e
  pelo roteiro manual em `docs/07-laudo/template-laudo-testador.md`.
- Cobertura de `admin.py` cobre os fluxos principais, não todos os ramos de erro.
