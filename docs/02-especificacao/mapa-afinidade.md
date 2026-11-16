# Mapa de afinidade

Agrupamento das 15 histórias por eixo temático (épico). O objetivo é permitir entrega
incremental por valor: cada épico fecha um conjunto coerente de telas e regras.

```mermaid
flowchart LR
  A["Épico A<br/>Conta e acesso"] --> A1[US-01 Cadastro]
  A --> A2[US-02 Login/logout]
  B["Épico B<br/>Vitrine e carrinho"] --> B1[US-03 Vitrine]
  B --> B2[US-04 Detalhe]
  B --> B3[US-05 Carrinho]
  C["Épico C<br/>Pedido e pagamento"] --> C1[US-06 Checkout]
  C --> C2[US-07 Pagamento]
  C --> C3[US-08 Acompanhamento]
  C --> C4[US-09 Cancelamento]
  D["Épico D<br/>Administração"] --> D1[US-10 Categorias]
  D --> D2[US-11 Produtos]
  D --> D3[US-12 Pedidos]
  D --> D4[US-13 Relatório]
  D --> D5[US-15 Usuários]
  E["Épico E<br/>Entrega"] --> E1[US-14 Entregas]
```

| Épico | Histórias | Pontos | Ator principal | Valor entregue |
|---|---|---|---|---|
| A — Conta e acesso | US-01, US-02 | 5 | Cliente | Identidade e sessão segura |
| B — Vitrine e carrinho | US-03, US-04, US-05 | 13 | Cliente | Descoberta e montagem do pedido |
| C — Pedido e pagamento | US-06, US-07, US-08, US-09 | 21 | Cliente | Conversão e pós-venda |
| D — Administração | US-10, US-11, US-12, US-13, US-15 | 24 | Administrador | Operação da loja |
| E — Entrega | US-14 | 5 | Entregador | Fechamento logístico |

## Leitura do mapa

- O épico C depende de A e B (não há pedido sem cliente nem carrinho).
- O épico D depende de B (produtos e categorias alimentam a vitrine) e de C (pedidos a
  operar).
- O épico E depende de C e D (entrega só existe para pedido pago e despachado).
- A ordem de implementação segue as ondas do backlog, não a ordem alfabética dos épicos.
