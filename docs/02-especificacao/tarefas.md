# Tarefas técnicas

Decomposição das histórias em tarefas de 2 a 12 horas. Nenhuma tarefa ultrapassa 12 h;
toda história tem ao menos uma tarefa. Tarefas `T-1xx` são habilitadoras (infraestrutura
e documentação) e não pertencem a uma história de usuário.

## Histórias

| ID | Tarefa | História | Horas |
|---|---|---|---|
| T-001 | Modelo `usuarios` + script de schema | US-01 | 4 |
| T-002 | Hash scrypt e validação de senha | US-01 | 3 |
| T-003 | Controller e template de cadastro | US-01 | 5 |
| T-004 | Testes de cadastro (CA1–CA5) | US-01 | 3 |
| T-005 | Sessão assinada + CSRF | US-02 | 4 |
| T-006 | Login/logout, controller e template | US-02 | 4 |
| T-007 | Guardas de rota e papéis | US-02 | 3 |
| T-008 | Testes de autenticação e autorização | US-02 | 3 |
| T-009 | Consultas de catálogo com busca e filtro | US-03 | 3 |
| T-010 | Template da vitrine e estados vazios | US-03 | 5 |
| T-011 | Testes de vitrine | US-03 | 3 |
| T-012 | Rota de detalhe por slug | US-04 | 2 |
| T-013 | Template de detalhe | US-04 | 3 |
| T-014 | Testes de detalhe e esgotado | US-04 | 2 |
| T-015 | Serviço de carrinho puro (sem I/O) | US-05 | 4 |
| T-016 | Rotas adicionar/atualizar/remover | US-05 | 4 |
| T-017 | Template do carrinho | US-05 | 4 |
| T-018 | Testes do carrinho | US-05 | 4 |
| T-019 | Serviço de frete e validação de endereço | US-06 | 3 |
| T-020 | Criação transacional do pedido | US-06 | 6 |
| T-021 | Template de checkout | US-06 | 5 |
| T-022 | Testes de checkout | US-06 | 4 |
| T-023 | Gateway simulado (Luhn e regra de recusa) | US-07 | 4 |
| T-024 | Transação de pagamento + baixa de estoque | US-07 | 6 |
| T-025 | Template de pagamento | US-07 | 4 |
| T-026 | Testes de pagamento e concorrência | US-07 | 5 |
| T-027 | Consultas de pedidos do cliente | US-08 | 3 |
| T-028 | Templates de lista e detalhe | US-08 | 5 |
| T-029 | Testes de isolamento entre clientes | US-08 | 3 |
| T-030 | Cancelamento com reposição idempotente | US-09 | 4 |
| T-031 | UI de confirmação com POST/CSRF | US-09 | 2 |
| T-032 | Testes de cancelamento | US-09 | 3 |
| T-033 | CRUD de categorias e slug | US-10 | 5 |
| T-034 | Templates de categorias | US-10 | 3 |
| T-035 | Testes de categorias | US-10 | 3 |
| T-036 | CRUD de produtos | US-11 | 6 |
| T-037 | Templates de produtos e formulário | US-11 | 5 |
| T-038 | Testes de produtos | US-11 | 4 |
| T-039 | Máquina de estados do pedido | US-12 | 4 |
| T-040 | Controller de status e atribuição de entregador | US-12 | 5 |
| T-041 | Templates de gestão de pedidos | US-12 | 4 |
| T-042 | Testes de transições válidas e inválidas | US-12 | 4 |
| T-043 | Consultas agregadas do relatório | US-13 | 4 |
| T-044 | Template do relatório | US-13 | 4 |
| T-045 | Testes de cálculo do relatório | US-13 | 3 |
| T-046 | Lista e detalhe de entregas | US-14 | 4 |
| T-047 | Confirmação de entrega | US-14 | 3 |
| T-048 | Testes da área do entregador | US-14 | 3 |
| T-049 | Gestão de papéis e ativação | US-15 | 4 |
| T-050 | Template de usuários | US-15 | 3 |
| T-051 | Testes de usuários | US-15 | 3 |
| T-052 | Preservar carrinho no login/cadastro | US-17 | 2 |
| T-053 | Área `/conta`: dados e senha | US-16 | 6 |
| T-054 | CRUD de endereços do cliente | US-16 | 5 |
| T-055 | Seleção explícita de endereço no checkout | US-19 | 5 |
| T-056 | Upload e remoção de imagem do produto | US-18 | 5 |
| T-057 | Exclusão lógica e lixeira de produtos | US-18 | 4 |
| T-058 | Cartões responsivos no admin | US-19 | 3 |
| T-059 | Correção de overflow do checkout | US-19 | 2 |
| T-060 | Divulgação do acesso do entregador | US-14 | 1 |
| T-061 | Testes de regressão do ciclo de feedback | US-16..19 | 6 |
| T-062 | Atualização de docs, laudo e dicionário | T-106 | 4 |

## Tarefas habilitadoras

| ID | Tarefa | Horas |
|---|---|---|
| T-100 | Estrutura do repositório, config, env, Makefile | 4 |
| T-101 | `schema.sql` + `seed.sql` + dicionário gerado | 8 |
| T-102 | Lint e tipagem (ruff, mypy strict, ESLint, Stylelint, sniff) | 6 |
| T-103 | Deploy com MariaDB gerenciado e health check | 6 |
| T-104 | UML, IHC e mapa de rastreabilidade | 12 |
| T-105 | Relatório de execução dos testes | 3 |
| T-106 | Template de laudo e consolidação dos 5 testadores | 6 |
| T-107 | Laudo de qualidade com evidências | 4 |

## Regra de estimativa

- Mínimo 2 h, máximo 12 h por tarefa.
- Tarefa acima de 12 h deve ser quebrada antes de entrar em execução.
- Horas são estimativas ideais; o registro real fica no histórico de commits.
