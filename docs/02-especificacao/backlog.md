# Product Backlog priorizado

Ordem de entrega definida por risco e valor: primeiro o fluxo que gera receita
(conta → vitrine → carrinho → checkout → pagamento → acompanhamento), depois a operação
(administração e entrega). Pontos em Fibonacci; prioridade A–E.

| # | ID | História | Épico | Pontos | Prioridade |
|---|---|---|---|---|---|
| 1 | US-01 | Cadastro de cliente | Conta e acesso | 3 | A |
| 2 | US-02 | Login e logout | Conta e acesso | 2 | A |
| 3 | US-03 | Vitrine com busca e filtro | Vitrine e carrinho | 5 | A |
| 4 | US-05 | Carrinho de compras | Vitrine e carrinho | 5 | A |
| 5 | US-06 | Checkout com endereço e frete | Pedido e pagamento | 8 | A |
| 6 | US-07 | Pagamento simulado | Pedido e pagamento | 5 | A |
| 7 | US-08 | Acompanhamento do pedido | Pedido e pagamento | 5 | A |
| 8 | US-11 | Administração de produtos e estoque | Administração | 5 | A |
| 9 | US-12 | Gestão de pedidos e status | Administração | 8 | A |
| 10 | US-04 | Detalhe do produto | Vitrine e carrinho | 3 | B |
| 11 | US-09 | Cancelamento pelo cliente | Pedido e pagamento | 3 | B |
| 12 | US-13 | Relatório de vendas | Administração | 5 | B |
| 13 | US-14 | Entregas do entregador | Entrega | 5 | B |
| 14 | US-10 | Administração de categorias | Administração | 3 | C |
| 15 | US-15 | Administração de usuários | Administração | 3 | C |

**Total:** 68 pontos.

## Distribuição em ondas

| Onda | Histórias | Objetivo |
|---|---|---|
| 1 — Contrato e dados | US-01, US-02, US-11, US-12 (modelo) | Banco, autenticação e catálogo administrativo |
| 2 — Fluxo do cliente | US-03, US-04, US-05, US-06, US-07, US-08, US-09 | Compra ponta a ponta |
| 3 — Operação | US-10, US-12, US-13, US-14, US-15 | Administração, relatório e entrega |

## Critério de corte

Se o prazo apertar, o corte desce a partir da prioridade C. As histórias A e B são
suficientes para o fluxo completo (compra, pagamento, acompanhamento, operação e
entrega). Nenhuma história A pode ser removida sem justificativa no histórico de
revisões, porque cada uma sustenta um critério de aceitação do enunciado.
