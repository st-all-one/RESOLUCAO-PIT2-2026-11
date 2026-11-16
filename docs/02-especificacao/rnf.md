# Requisitos não funcionais

Todo RNF tem métrica e forma de verificação. RNF sem métrica não entra no catálogo.

## Desempenho

| ID | Requisito | Métrica | Verificação |
|---|---|---|---|
| RNF-DES-01 | Páginas principais respondem rápido com o seed carregado | p95 < 500 ms em 100 requisições locais | Script de carga simples no relatório de testes |
| RNF-DES-02 | Página inicial leve | < 300 KB transferidos, sem dependência externa | Aba Network / `du` dos assets |

## Segurança

| ID | Requisito | Métrica | Verificação |
|---|---|---|---|
| RNF-SEG-01 | Senha nunca armazenada em claro | scrypt (N=16384, r=8, p=1), salt de 16 bytes | Inspeção do banco + teste unitário |
| RNF-SEG-02 | Sessão protegida | Cookie `HttpOnly`, `SameSite=Lax`, `Secure` em produção, expiração de 24 h | Cabeçalho `Set-Cookie` + configuração |
| RNF-SEG-03 | CSRF em toda mutação por formulário | Token de sessão validado; ausência → 403 `ERR-AUTH-008` | Teste de POST sem token |
| RNF-SEG-04 | Autorização no servidor | Toda rota de papel restrito retorna 403 para papel incorreto | Testes por papel |
| RNF-SEG-05 | Nenhum segredo versionado | `.env` ignorado; `.env.example` sem valores reais | `git grep` por padrões de chave |
| RNF-SEG-06 | Entrada validada e limitada | Nome ≤ 120, descrição ≤ 2000, alergênicos ≤ 255, telefone 10–11 dígitos | Testes de limite |
| RNF-SEG-07 | Nenhum dado completo de cartão persistido | Apenas últimos 4 dígitos e código de autorização | Inspeção do schema |

## Usabilidade e acessibilidade

| ID | Requisito | Métrica | Verificação |
|---|---|---|---|
| RNF-USA-01 | Mobile-first | Sem scroll horizontal em viewport 360×640 e 390×844 | Verificação visual + sniff |
| RNF-USA-02 | Contraste e foco | Texto normal ≥ 4.5:1; foco visível em todos os controles | sniff check + inspeção |
| RNF-USA-03 | Teclado e rótulos | Todos os campos com `label` associado; fluxo completo por teclado | sniff check + navegação manual |
| RNF-USA-04 | Mensagens acionáveis | Toda validação exibe código, causa e ação do catálogo | Testes que verificam `data-codigo` |

## Disponibilidade e operação

| ID | Requisito | Métrica | Verificação |
|---|---|---|---|
| RNF-DIS-01 | Health check | `GET /health` → 200 com `{status, db}` em < 1 s | Teste + verificação pós-deploy |
| RNF-DIS-02 | Erro sem vazamento | Nenhuma stack trace na resposta; erro genérico `ERR-SYS-001` | Teste de exceção forçada |
| RNF-OBS-01 | Log sem PII | Log não contém e-mail, senha, endereço completo nem PAN | Revisão do logger + teste |

## Manutenibilidade e dados

| ID | Requisito | Métrica | Verificação |
|---|---|---|---|
| RNF-MAN-01 | Lint e tipos sem erros | ruff, mypy strict, ESLint strict-type-checked e Stylelint com 0 erros | `make check` |
| RNF-MAN-02 | Cobertura de testes | ≥ 80% das linhas de `src/app` | `pytest --cov` |
| RNF-DAD-01 | Integridade no banco | PK, FK, UNIQUE e CHECK no `schema.sql`; nenhuma regra só na aplicação | `schema.sql` + testes de violação |
| RNF-DAD-02 | Atomicidade | Checkout, pagamento e cancelamento alteram pedido, itens, pagamento e estoque na mesma transação | Testes de falha induzida |
| RNF-DAD-03 | Normalização | Nenhuma tabela em violação de 3FN | Revisão do modelo lógico |

## Compatibilidade

| ID | Requisito | Métrica | Verificação |
|---|---|---|---|
| RNF-COM-01 | Navegadores atuais | Chrome/Chromium e Firefox nas duas últimas versões | Teste manual |
| RNF-COM-02 | SGBD suportado | MySQL 8.4 | `schema.sql` executado do zero |
