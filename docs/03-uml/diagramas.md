# Diagramas UML — Cupcake Gourmet 2.0

Diagramas de apoio à implementação. Todos refletem o código em `backend/app` e o
schema em `database/schema.sql`.

## Casos de uso

```mermaid
flowchart LR
  cliente([Cliente])
  admin([Administrador])
  entregador([Entregador])

  cliente --> uc1[Ver vitrine, buscar e filtrar]
  cliente --> uc2[Ver detalhe do produto]
  cliente --> uc3[Gerenciar carrinho]
  cliente --> uc4[Finalizar pedido com endereço]
  cliente --> uc5[Pagar com PIX ou cartão simulado]
  cliente --> uc6[Acompanhar e cancelar pedido]
  cliente --> uc7[Cadastrar-se e autenticar-se]

  admin --> uc8[Gerenciar categorias]
  admin --> uc9[Gerenciar produtos e estoque]
  admin --> uc10[Gerir pedidos e status]
  admin --> uc11[Consultar relatório de vendas]
  admin --> uc12[Gerir usuários e papéis]

  entregador --> uc13[Ver entregas atribuídas]
  entregador --> uc14[Confirmar entrega]
```

## Componentes (MVC)

```mermaid
flowchart TB
  navegador[Navegador<br/>HTML + CSS + TS] -->|HTTP| app[FastAPI]
  app --> contexto[ContextoMiddleware<br/>sessão, usuário, flash, carrinho]
  contexto --> controllers[Controllers<br/>auth, catálogo, carrinho, checkout,<br/>pagamento, pedidos, admin, entregas]
  controllers --> services[Services<br/>preço, carrinho, pedido, pagamento,<br/>slug, validação, segurança, operações]
  controllers --> models[Models SQLAlchemy]
  services --> models
  models --> mariadb[(MariaDB 11.4)]
  controllers --> templates[Jinja2<br/>mobile-first]
  templates --> navegador
```

## Classes do domínio

```mermaid
classDiagram
  class Usuario {
    +int id
    +str nome
    +str email
    +str senha_hash
    +str papel
    +bool ativo
    +eh_admin() bool
  }
  class Endereco {
    +int id
    +str cep
    +str logradouro
    +str numero
    +str bairro
    +str cidade
    +str uf
    +bool principal
  }
  class Categoria {
    +int id
    +str nome
    +str slug
    +bool ativo
  }
  class Produto {
    +int id
    +str nome
    +str slug
    +Decimal preco
    +int estoque
    +bool ativo
    +esgotado() bool
  }
  class Pedido {
    +int id
    +str status
    +Decimal frete
    +subtotal() Decimal
    +total() Decimal
    +pago() bool
  }
  class ItemPedido {
    +str nome_produto
    +Decimal preco_unitario
    +int quantidade
    +subtotal() Decimal
  }
  class Pagamento {
    +str metodo
    +str status
    +Decimal valor
    +str cartao_ultimos4
    +str codigo_autorizacao
  }
  class HistoricoPedido {
    +str status
    +str observacao
    +datetime criado_em
  }

  Usuario "1" --> "0..*" Endereco
  Usuario "1" --> "0..*" Pedido : cliente
  Usuario "0..1" --> "0..*" Pedido : entregador
  Categoria "1" --> "0..*" Produto
  Pedido "1" --> "1..*" ItemPedido
  Produto "1" --> "0..*" ItemPedido
  Pedido "1" --> "0..1" Pagamento
  Pedido "1" --> "0..*" HistoricoPedido
```

## Estados do pedido

```mermaid
stateDiagram-v2
  [*] --> recebido
  recebido --> em_preparo: pagamento aprovado
  recebido --> cancelado: cliente ou admin
  em_preparo --> saiu_entrega: entregador definido
  em_preparo --> cancelado: admin
  saiu_entrega --> entregue: confirmação do entregador
  saiu_entrega --> cancelado: admin
  entregue --> [*]
  cancelado --> [*]
```

## Sequência — checkout e pagamento

```mermaid
sequenceDiagram
  actor C as Cliente
  participant CC as CheckoutController
  participant CS as CarrinhoService
  participant PC as PagamentoController
  participant PS as PagamentoService
  participant DB as MariaDB

  C->>CC: POST /checkout (endereço)
  CC->>CS: ler carrinho da sessão
  CS-->>CC: itens + quantidades
  CC->>CC: valida CEP, UF, telefone e estoque
  CC->>DB: INSERT pedido, itens, pagamento pendente, histórico
  DB-->>CC: pedido criado
  CC-->>C: 303 /pedidos/{id}/pagamento

  C->>PC: POST /pedidos/{id}/pagamento (pix/cartão)
  PC->>PS: simular(metodo, numero)
  PS-->>PC: aprovado/recusado + código
  alt aprovado
    PC->>DB: UPDATE produtos SET estoque = estoque - qtd (condicional)
    PC->>DB: UPDATE pagamento aprovado + histórico
    PC-->>C: 303 /pedidos/{id}
  else recusado
    PC->>DB: UPDATE pagamento recusado
    PC-->>C: 303 /pedidos/{id}/pagamento com flash ERR-PAG-001
  end
```
