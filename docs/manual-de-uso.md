# Manual de uso — Cupcake Gourmet 2.0

Aplicação mobile-first: as telas foram desenhadas para 360 px e se expandem em
grade a partir de 48 rem. Todos os fluxos funcionam por teclado e sem JavaScript;
o TypeScript apenas melhora confirmações e o formulário de cartão.

## Contas de demonstração

| Papel | E-mail | Senha |
|---|---|---|
| Administrador | `admin@cupcake.projeto` | `adminCupcake` |
| Cliente | `cliente@cupcake.local` | `Cliente@123` |
| Entregador | `entregador@cupcake.local` | `Entrega@123` |

As mesmas contas aparecem na tela de login, em “Contas de demonstração”, para
facilitar o teste dos três papéis.

## Cliente

1. **Vitrine** (`/`): busca por texto, filtro por categoria e cartões com preço,
   alergênicos e indicação de esgotado.
2. **Detalhe** (`/produtos/{slug}`): descrição, estoque e botão de adicionar.
3. **Carrinho** (`/carrinho`): altere quantidades ou remova itens. Subtotal,
   frete (R$ 8,00; grátis a partir de R$ 120,00) e total são recalculados no
   servidor. O carrinho montado como visitante é preservado ao entrar ou criar
   conta.
4. **Checkout** (`/checkout`): se a conta tem endereços salvos, escolha um deles
   ou “Outro endereço” e confira o texto exibido; o telefone da conta aparece em
   campo próprio. O CEP preenche o endereço automaticamente e as quantidades
   podem ser ajustadas no resumo; o pedido é criado com pagamento pendente.
5. **Pagamento** (`/pedidos/{codigo}/pagamento`): PIX aprova na hora. Cartão exige
   número com Luhn válido; cartão terminado em `0000` é recusado (simulação).
   Nenhum dado completo de cartão é armazenado.
6. **Pedidos** (`/pedidos`): lista, detalhe com linha do tempo e cancelamento
   enquanto o status for "Recebido" (estoque e pagamento são estornados).
7. **Minha conta** (`/conta`): altere nome, e-mail e telefone; troque a senha
   (as outras sessões são encerradas); adicione, promova a principal ou remova
   endereços de entrega.

## Administrador

Acesse `/admin` após entrar com a conta de administrador.

- **Produtos**: criar, editar, ativar/desativar e excluir. A imagem aceita JPG,
  PNG ou WebP de até 2 MB, com prévia e opção de remover. A exclusão é lógica:
  o item sai da vitrine e vai para a **Lixeira**, onde pode ser restaurado com
  todo o histórico. O estoque é editável; preço aceita vírgula ou ponto.
  No celular, a lista vira cartões com as ações em botões de toque.
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

- Entre em `/entregas` (a tela inicial de login mostra a conta de demonstração).
- Lista apenas pedidos atribuídos a você que estejam "Saiu para entrega". Se a
  lista estiver vazia, o administrador ainda não atribuiu nenhum pedido a você.
- Detalhe mostra endereço, telefone clicável, itens e total.
- **Confirmar entrega** muda o status para "Entregue" e registra o evento na
  linha do tempo do cliente.

## Mensagens

Toda mensagem de erro tem código estável (ex.: `ERR-PAG-001`) visível na tela e
o detalhe em `docs/04-ihc/mensagens-erro.md`. Requisições com
`Accept: application/problem+json` recebem Problem Details RFC 9457.
