# Dicionário de dados

> Gerado automaticamente de `information_schema` em 2026-11-15 22:17. Não editar à mão: rode `make dicionario`.

## Resumo

| Tabela | Colunas | Restrições CHECK |
|---|---|---|
| `categorias` | 5 | 0 |
| `enderecos` | 11 | 2 |
| `historico_pedido` | 6 | 1 |
| `itens_pedido` | 6 | 2 |
| `pagamentos` | 9 | 3 |
| `pedidos` | 15 | 3 |
| `produtos` | 11 | 4 |
| `usuarios` | 9 | 2 |

## `categorias`

| Coluna | Tipo | Nulo? | Default | Chave / Domínio | Descrição |
|---|---|---|---|---|---|
| `id` | `bigint(20) unsigned` | não | — (auto_increment) | PK | Identificador interno da categoria. |
| `nome` | `varchar(80)` | não | — | UQ | Nome exibido na vitrine. |
| `slug` | `varchar(80)` | não | — | UQ | Identificador textual usado na URL. |
| `ativo` | `tinyint(1)` | não | `1` | 0 = oculta, 1 = visível | Indica se a categoria aparece na vitrine. |
| `criado_em` | `timestamp` | não | `current_timestamp()` | — | Data e hora de criação. |

## `enderecos`

| Coluna | Tipo | Nulo? | Default | Chave / Domínio | Descrição |
|---|---|---|---|---|---|
| `id` | `bigint(20) unsigned` | não | — (auto_increment) | PK | Identificador interno do endereço. |
| `usuario_id` | `bigint(20) unsigned` | não | — | FK → usuarios.id | Dono do endereço. |
| `cep` | `char(8)` | não | — | 8 dígitos | CEP com 8 dígitos, sem hífen. |
| `logradouro` | `varchar(160)` | não | — | — | Rua, avenida ou praça. |
| `numero` | `varchar(20)` | não | — | — | Número do imóvel. |
| `complemento` | `varchar(80)` | sim | `NULL` | — | Apartamento, bloco ou referência. |
| `bairro` | `varchar(80)` | não | — | — | Bairro do endereço. |
| `cidade` | `varchar(80)` | não | — | — | Cidade do endereço. |
| `uf` | `char(2)` | não | — | 2 letras maiúsculas | Unidade federativa com 2 letras maiúsculas. |
| `principal` | `tinyint(1)` | não | `0` | 0 = alternativo, 1 = padrão | Indica o endereço padrão do usuário. |
| `criado_em` | `timestamp` | não | `current_timestamp()` | — | Data e hora de criação. |

**Restrições CHECK:**

- `ck_enderecos_cep`: ``cep` regexp '^[0-9]{8}$'`
- `ck_enderecos_uf`: ``uf` regexp '^[A-Z]{2}$'`

## `historico_pedido`

| Coluna | Tipo | Nulo? | Default | Chave / Domínio | Descrição |
|---|---|---|---|---|---|
| `id` | `bigint(20) unsigned` | não | — (auto_increment) | PK | Identificador interno do evento. |
| `pedido_id` | `bigint(20) unsigned` | não | — | FK → pedidos.id | Pedido ao qual o evento se refere. |
| `status` | `varchar(20)` | não | — | recebido | em_preparo | saiu_entrega | entregue | cancelado | Status registrado no evento. |
| `usuario_id` | `bigint(20) unsigned` | sim | `NULL` | FK → usuarios.id | Quem provocou a transição. |
| `observacao` | `varchar(255)` | sim | `NULL` | — | Nota livre sobre a transição. |
| `criado_em` | `timestamp` | não | `current_timestamp()` | — | Data e hora do evento. |

**Restrições CHECK:**

- `ck_historico_status`: ``status` in ('recebido','em_preparo','saiu_entrega','entregue','cancelado')`

## `itens_pedido`

| Coluna | Tipo | Nulo? | Default | Chave / Domínio | Descrição |
|---|---|---|---|---|---|
| `id` | `bigint(20) unsigned` | não | — (auto_increment) | PK | Identificador interno do item. |
| `pedido_id` | `bigint(20) unsigned` | não | — | UQ · FK → pedidos.id | Pedido ao qual o item pertence. |
| `produto_id` | `bigint(20) unsigned` | não | — | UQ · FK → produtos.id | Produto comprado. |
| `nome_produto` | `varchar(120)` | não | — | — | Nome do produto no momento da compra (snapshot). |
| `preco_unitario` | `decimal(10,2)` | não | — | > 0 | Preço unitário no momento da compra (snapshot). |
| `quantidade` | `int(11)` | não | — | > 0 | Quantidade comprada do produto. |

**Restrições CHECK:**

- `ck_itens_preco`: ``preco_unitario` > 0`
- `ck_itens_quantidade`: ``quantidade` > 0`

## `pagamentos`

| Coluna | Tipo | Nulo? | Default | Chave / Domínio | Descrição |
|---|---|---|---|---|---|
| `id` | `bigint(20) unsigned` | não | — (auto_increment) | PK | Identificador interno do pagamento. |
| `pedido_id` | `bigint(20) unsigned` | não | — | UQ · FK → pedidos.id | Pedido pago; relação um para um. |
| `metodo` | `varchar(20)` | sim | `NULL` | pix | cartao | Meio de pagamento escolhido. |
| `status` | `varchar(20)` | não | `'pendente'` | pendente | aprovado | recusado | estornado | cancelado | Estado do pagamento. |
| `valor` | `decimal(10,2)` | não | — | > 0 | Montante autorizado no ato do pagamento. |
| `cartao_ultimos4` | `char(4)` | sim | `NULL` | 4 dígitos quando metodo = cartao | Últimos 4 dígitos do cartão; nunca o número completo. |
| `codigo_autorizacao` | `varchar(40)` | sim | `NULL` | — | Código devolvido pela operadora simulada. |
| `criado_em` | `timestamp` | não | `current_timestamp()` | — | Data e hora de criação do pagamento. |
| `atualizado_em` | `timestamp` | não | `current_timestamp()` (on update current_timestamp()) | — | Data e hora da última alteração. |

**Restrições CHECK:**

- `ck_pagamentos_metodo`: ``metodo` is null or `metodo` in ('pix','cartao')`
- `ck_pagamentos_status`: ``status` in ('pendente','aprovado','recusado','estornado','cancelado')`
- `ck_pagamentos_valor`: ``valor` > 0`

## `pedidos`

| Coluna | Tipo | Nulo? | Default | Chave / Domínio | Descrição |
|---|---|---|---|---|---|
| `id` | `bigint(20) unsigned` | não | — (auto_increment) | PK | Identificador interno do pedido. |
| `cliente_id` | `bigint(20) unsigned` | não | — | FK → usuarios.id | Cliente que realizou o pedido. |
| `entregador_id` | `bigint(20) unsigned` | sim | `NULL` | FK → usuarios.id | Entregador atribuído ao despacho. |
| `status` | `varchar(20)` | não | `'recebido'` | recebido | em_preparo | saiu_entrega | entregue | cancelado | Estado atual do pedido na máquina de estados. |
| `frete` | `decimal(10,2)` | não | `0.00` | >= 0 | Valor do frete cobrado no momento do pedido. |
| `cep` | `char(8)` | não | — | — | CEP do endereço de entrega (snapshot). |
| `logradouro` | `varchar(160)` | não | — | — | Logradouro de entrega (snapshot). |
| `numero` | `varchar(20)` | não | — | — | Número de entrega (snapshot). |
| `complemento` | `varchar(80)` | sim | `NULL` | — | Complemento de entrega (snapshot). |
| `bairro` | `varchar(80)` | não | — | — | Bairro de entrega (snapshot). |
| `cidade` | `varchar(80)` | não | — | — | Cidade de entrega (snapshot). |
| `uf` | `char(2)` | não | — | 2 letras maiúsculas | UF de entrega (snapshot). |
| `telefone_contato` | `varchar(11)` | não | — | — | Telefone para contato na entrega (snapshot). |
| `criado_em` | `timestamp` | não | `current_timestamp()` | — | Data e hora da criação do pedido. |
| `atualizado_em` | `timestamp` | não | `current_timestamp()` (on update current_timestamp()) | — | Data e hora da última mudança de estado. |

**Restrições CHECK:**

- `ck_pedidos_frete`: ``frete` >= 0`
- `ck_pedidos_status`: ``status` in ('recebido','em_preparo','saiu_entrega','entregue','cancelado')`
- `ck_pedidos_uf`: ``uf` regexp '^[A-Z]{2}$'`

## `produtos`

| Coluna | Tipo | Nulo? | Default | Chave / Domínio | Descrição |
|---|---|---|---|---|---|
| `id` | `bigint(20) unsigned` | não | — (auto_increment) | PK | Identificador interno do produto. |
| `categoria_id` | `bigint(20) unsigned` | não | — | FK → categorias.id | Categoria à qual o produto pertence. |
| `nome` | `varchar(120)` | não | — | — | Nome comercial do cupcake. |
| `slug` | `varchar(140)` | não | — | UQ | Identificador textual usado na URL do detalhe. |
| `descricao` | `text` | não | — | — | Descrição comercial do produto. |
| `alergenicos` | `varchar(255)` | não | — | — | Ingredientes alergênicos declarados. |
| `preco` | `decimal(10,2)` | não | — | > 0, duas casas decimais | Preço unitário vigente em reais. |
| `estoque` | `int(11)` | não | `0` | >= 0 | Quantidade disponível para venda. |
| `ativo` | `tinyint(1)` | não | `1` | 0 = oculto, 1 = visível | Indica se o produto aparece na vitrine. |
| `criado_em` | `timestamp` | não | `current_timestamp()` | — | Data e hora de criação. |
| `atualizado_em` | `timestamp` | não | `current_timestamp()` (on update current_timestamp()) | — | Data e hora da última alteração. |

**Restrições CHECK:**

- `ck_produtos_descricao`: `char_length(`descricao`) between 1 and 2000`
- `ck_produtos_estoque`: ``estoque` >= 0`
- `ck_produtos_nome`: `char_length(`nome`) between 2 and 120`
- `ck_produtos_preco`: ``preco` > 0`

## `usuarios`

| Coluna | Tipo | Nulo? | Default | Chave / Domínio | Descrição |
|---|---|---|---|---|---|
| `id` | `bigint(20) unsigned` | não | — (auto_increment) | PK | Identificador interno da conta. |
| `nome` | `varchar(120)` | não | — | — | Nome de exibição da pessoa. |
| `email` | `varchar(254)` | não | — | UQ | Identidade de login; normalizado em minúsculas. |
| `senha_hash` | `varchar(255)` | não | — | — | Hash scrypt da senha com salt; nunca a senha em claro. |
| `telefone` | `varchar(11)` | sim | `NULL` | — | Telefone de contato com DDD, somente dígitos. |
| `papel` | `varchar(20)` | não | `'cliente'` | cliente | entregador | admin | Perfil de acesso do usuário. |
| `ativo` | `tinyint(1)` | não | `1` | 0 = inativo, 1 = ativo | Indica se a conta pode autenticar. |
| `criado_em` | `timestamp` | não | `current_timestamp()` | — | Data e hora de criação da conta. |
| `atualizado_em` | `timestamp` | não | `current_timestamp()` (on update current_timestamp()) | — | Data e hora da última alteração. |

**Restrições CHECK:**

- `ck_usuarios_nome`: `char_length(`nome`) between 2 and 120`
- `ck_usuarios_papel`: ``papel` in ('cliente','entregador','admin')`
