# Projeto lógico normalizado

Derivação do modelo conceitual para o relacional, com chaves e justificativa de
normalização. O projeto físico correspondente está em [`database/schema.sql`](../../database/schema.sql).

## Tabelas

| Tabela | PK | Chaves estrangeiras | Chaves únicas |
|---|---|---|---|
| `usuarios` | `id` | — | `email` |
| `categorias` | `id` | — | `nome`, `slug` |
| `produtos` | `id` | `categoria_id → categorias.id` | `slug` |
| `enderecos` | `id` | `usuario_id → usuarios.id` | — |
| `pedidos` | `id` | `cliente_id → usuarios.id`, `entregador_id → usuarios.id` | — |
| `itens_pedido` | `id` | `pedido_id → pedidos.id`, `produto_id → produtos.id` | (`pedido_id`, `produto_id`) |
| `pagamentos` | `id` | `pedido_id → pedidos.id` | `pedido_id` |
| `historico_pedido` | `id` | `pedido_id → pedidos.id`, `usuario_id → usuarios.id` | — |

## Normalização

### Primeira forma normal (1FN)

Todos os atributos são atômicos. Não há listas repetidas: os itens do pedido vivem em
`itens_pedido`, e o endereço é decomposto em colunas atômicas (CEP, logradouro, número,
complemento, bairro, cidade, UF). O telefone é um valor único por pedido.

### Segunda forma normal (2FN)

Toda tabela tem chave primária simples (`id`), exceto a unicidade composta de
`itens_pedido (pedido_id, produto_id)`, que é uma restrição de integridade, não a PK.
Com PK simples, não existem dependências parciais de chave composta.

### Terceira forma normal (3FN)

Não há dependências transitivas entre atributos não-chave:

- totais do pedido (`subtotal`, `total`) **não são armazenados**; são calculados a partir
  de `itens_pedido.preco_unitario × quantidade` mais `pedidos.frete`;
- o nome da categoria não é copiado em `produtos`; vem por junção;
- o nome do cliente não é copiado em `pedidos`; vem por junção;
- o status atual do pedido não é duplicado no histórico; o histórico é uma trilha de
  eventos, e o status vigente fica em `pedidos.status`.

## Snapshots históricos (exceção consciente)

Dois grupos de colunas copiam valores no momento do fato. Não são dependências
transitivas do estado atual, e sim atributos do evento:

| Coluna | Por que existe | Por que não viola 3FN |
|---|---|---|
| `itens_pedido.nome_produto` | Preserva o nome vendido | Descreve o item no instante da compra, não o produto atual |
| `itens_pedido.preco_unitario` | Preserva o preço praticado | Idem; o preço do produto pode mudar depois |
| `pedidos.cep … uf`, `telefone_contato` | Preserva o destino da entrega | Endereço do pedido é imutável; o cadastro do cliente pode mudar |
| `pagamentos.valor` | Registra o montante autorizado | Fato do pagamento, não derivável se o pedido for alterado |
| `pedidos.frete` | Registra a regra aplicada no fechamento | A regra de frete pode mudar; o pedido mantém o valor contratado |

## Regras de integridade no banco

- `UNIQUE` em e-mail, nome/slug de categoria e slug de produto.
- `CHECK` de domínio em papéis, status, método de pagamento, preço > 0, estoque ≥ 0,
  quantidade > 0, CEP com 8 dígitos e UF com 2 letras.
- `FOREIGN KEY` com `RESTRICT` onde a exclusão destruiria histórico (categoria com
  produtos, produto com itens) e `CASCADE` onde o filho não existe sem o pai
  (itens, pagamento, histórico).
- `ON DELETE SET NULL` no entregador e no autor do histórico, preservando o pedido.

## Índices

| Índice | Consulta que atende |
|---|---|
| `ix_produtos_categoria`, `ix_produtos_ativo` | Vitrine por categoria e filtro de ativos |
| `ix_pedidos_cliente (cliente_id, criado_em)` | "Meus pedidos" ordenado por data |
| `ix_pedidos_status` | Gestão administrativa por status |
| `ix_pedidos_entregador` | Entregas atribuídas |
| `ix_historico_pedido (pedido_id, criado_em)` | Linha do tempo do pedido |
| `UNIQUE itens_pedido (pedido_id, produto_id)` | Impede item duplicado no mesmo pedido |

## Dicionário

O dicionário de dados é gerado do `information_schema` e cobre 100% das colunas:
[`dicionario.md`](dicionario.md).
