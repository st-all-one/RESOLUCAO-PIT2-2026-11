# Manual de uso — Cupcake Gourmet 2.0

Aplicação mobile-first: as telas foram desenhadas para 360 px e se expandem em
grade a partir de 48 rem. Todos os fluxos funcionam por teclado e sem JavaScript;
o TypeScript apenas melhora confirmações e o formulário de cartão.

## Contas de demonstração

| Papel | E-mail | Senha |
|---|---|---|
| Administrador | `admin@cupcake.local` | `Admin@123` |
| Cliente | `cliente@cupcake.local` | `Cliente@123` |
| Entregador | `entregador@cupcake.local` | `Entrega@123` |

## Cliente

1. **Vitrine** (`/`): busca por texto, filtro por categoria e cartões com preço,
   alergênicos e indicação de esgotado.
2. **Detalhe** (`/produtos/{slug}`): descrição, estoque e botão de adicionar.
3. **Carrinho** (`/carrinho`): altere quantidades ou remova itens. Subtotal,
   frete (R$ 8,00; grátis a partir de R$ 120,00) e total são recalculados no
   servidor.
4. **Checkout** (`/checkout`): informe o CEP para preencher o endereço e ajuste
   quantidades no próprio resumo; o pedido é criado com pagamento pendente.
5. **Pagamento** (`/pedidos/{codigo}/pagamento`): PIX aprova na hora. Cartão exige
   número com Luhn válido; cartão terminado em `0000` é recusado (simulação).
   Nenhum dado completo de cartão é armazenado.
6. **Pedidos** (`/pedidos`): lista, detalhe com linha do tempo e cancelamento
   enquanto o status for "Recebido" (estoque e pagamento são estornados).

## Administrador

Acesse `/admin` após entrar com a conta de administrador.

- **Produtos**: criar, editar, ativar/desativar e excluir (bloqueado se houver
  pedidos). O estoque é editável; preço aceita vírgula ou ponto.
- **Categorias**: criar, renomear, ativar/desativar e excluir (bloqueado se
  houver produtos).
- **Pedidos**: filtrar por status, abrir o pedido, avançar o status e escolher o
  entregador ao marcar "Saiu para entrega". Cancelamento estorna pagamento e
  estoque.
- **Relatório**: período inicial/final, pedidos pagos, receita, ticket médio e
  cinco produtos mais vendidos.
- **Usuários**: alternar papel entre cliente e entregador, ativar/desativar
  contas. O sistema impede que o administrador desative a própria conta ou
  rebaixe o último administrador ativo.

## Entregador

Acesse `/entregas` após entrar com a conta de entregador.

- Lista apenas pedidos atribuídos a você que estejam "Saiu para entrega".
- Detalhe mostra endereço, telefone clicável, itens e total.
- **Confirmar entrega** muda o status para "Entregue" e registra o evento na
  linha do tempo do cliente.

## Mensagens

Toda mensagem de erro tem código estável (ex.: `ERR-PAG-001`) visível na tela e
o detalhe em `docs/04-ihc/mensagens-erro.md`. Requisições com
`Accept: application/problem+json` recebem Problem Details RFC 9457.
