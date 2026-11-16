# Cartões de história — Cupcake Gourmet 2.0

Template T1 do plano. Convenções:

- **Prioridade:** A (indispensável) → E (desejável).
- **Pontos:** escala Fibonacci (1, 2, 3, 5, 8).
- **CA:** critério de aceitação em DADA/QUANDO/ENTÃO, verificável por teste.
- **RN:** regra de negócio imposta no servidor/banco.
- **RNF:** referência ao catálogo `rnf.md`.
- **Telas:** identificadores do mapa navegacional (`04-ihc/`).

---

## Épico A — Conta e acesso

### US-01 — Cadastro de cliente

**Requerente:** Cliente · **Prioridade:** A · **Pontos:** 3 · **Telas:** TELA-002

**Ação:** Como visitante, eu quero criar uma conta com nome, e-mail e senha, para que eu
possa comprar sem repetir meus dados a cada pedido.

**Comentários:** O e-mail é a identidade de login. Não há login social nem confirmação
por e-mail (fora de escopo).

**Critérios de aceitação**
- CA1 — DADA a tela de cadastro, QUANDO informo nome (2–120 caracteres), e-mail válido
  inédito, senha forte e confirmação igual, ENTÃO a conta é criada, a sessão é iniciada
  e sou levado à vitrine.
- CA2 — DADO um e-mail já cadastrado em qualquer caixa, QUANDO envio o cadastro, ENTÃO
  vejo `ERR-AUTH-002` e o formulário preserva nome e e-mail.
- CA3 — DADA uma senha com menos de 8 caracteres ou sem letra ou sem número, QUANDO
  envio, ENTÃO vejo `ERR-AUTH-003` e nenhum registro é gravado.
- CA4 — DADA confirmação diferente da senha, QUANDO envio, ENTÃO vejo `ERR-AUTH-004`.
- CA5 — DADO nome vazio ou e-mail malformado, QUANDO envio, ENTÃO vejo `ERR-AUTH-005`.

**Regras de negócio**
- RN1 — E-mail normalizado (trim + minúsculas) e único com comparação case-insensitive.
- RN2 — Senha armazenada apenas como hash scrypt com salt aleatório de 16 bytes.
- RN3 — Todo cadastro nasce com papel `cliente` e `ativo = true`.
- RN4 — Nome entre 2 e 120 caracteres.

**RNF:** RNF-SEG-01, RNF-SEG-06, RNF-USA-03.

---

### US-02 — Login e logout

**Requerente:** Cliente · **Prioridade:** A · **Pontos:** 2 · **Telas:** TELA-001

**Ação:** Como usuário cadastrado, eu quero entrar e sair da minha conta, para acessar
minhas áreas com segurança.

**Critérios de aceitação**
- CA1 — DADAS credenciais válidas de conta ativa, QUANDO envio o login, ENTÃO a sessão
  é iniciada e sou levado ao destino interno informado em `next` ou à vitrine.
- CA2 — DADAS credenciais inválidas, QUANDO envio o login, ENTÃO vejo `ERR-AUTH-001`
  sem indicação de qual campo está errado.
- CA3 — DADA uma conta com `ativo = false`, QUANDO envio credenciais corretas, ENTÃO
  vejo `ERR-AUTH-006` e nenhuma sessão é criada.
- CA4 — DADO que estou autenticado, QUANDO solicito logout, ENTÃO a sessão é limpa e
  rotas protegidas passam a redirecionar ao login.
- CA5 — DADO um acesso anônimo a rota protegida, QUANDO a requisição chega, ENTÃO sou
  redirecionado ao login com `next` seguro (apenas caminho interno).

**Regras de negócio**
- RN1 — A sessão é regenerada no login para impedir fixação de sessão.
- RN2 — `next` só aceita caminhos internos iniciados por `/`.
- RN3 — Comparação de hash em tempo constante.

**RNF:** RNF-SEG-02, RNF-SEG-03, RNF-SEG-04.

---

## Épico B — Vitrine e carrinho

### US-03 — Vitrine com busca e filtro

**Requerente:** Cliente · **Prioridade:** A · **Pontos:** 5 · **Telas:** TELA-003

**Ação:** Como cliente, eu quero navegar pelos cupcakes, buscar por nome e filtrar por
categoria, para encontrar rapidamente o que desejo comprar.

**Critérios de aceitação**
- CA1 — DADA a vitrine, QUANDO ela carrega, ENTÃO exibe somente produtos ativos com
  nome, categoria, preço em BRL e estado de estoque.
- CA2 — DADO o termo `q`, QUANDO busco, ENTÃO vejo produtos cujo nome ou descrição
  contenham o termo, sem diferenciar maiúsculas de minúsculas.
- CA3 — DADO um filtro de categoria, QUANDO o combino com busca, ENTÃO os dois critérios
  são aplicados em conjunto.
- CA4 — DADA uma busca sem resultado, QUANDO a página carrega, ENTÃO vejo estado vazio
  com o termo pesquisado e link para limpar filtros.
- CA5 — DADO um produto com estoque zero, QUANDO ele aparece na vitrine, ENTÃO é
  marcado como esgotado e não oferece adicionar ao carrinho.

**Regras de negócio**
- RN1 — Apenas produtos e categorias ativos aparecem.
- RN2 — Ordenação padrão por nome crescente.
- RN3 — Preço sempre formatado a partir do valor do banco (DECIMAL).

**RNF:** RNF-DES-01, RNF-USA-01.

---

### US-04 — Detalhe do produto

**Requerente:** Cliente · **Prioridade:** B · **Pontos:** 3 · **Telas:** TELA-004

**Ação:** Como cliente, eu quero ver os detalhes de um cupcake, para decidir com
informação de preço, descrição e alergênicos.

**Critérios de aceitação**
- CA1 — DADO um slug válido de produto ativo, QUANDO abro o detalhe, ENTÃO vejo nome,
  categoria, descrição, alergênicos, preço e disponibilidade.
- CA2 — DADO um slug inexistente ou de produto inativo, QUANDO abro a URL, ENTÃO recebo
  404 com `ERR-CAT-001`.
- CA3 — DADO um produto esgotado, QUANDO abro o detalhe, ENTÃO o botão de adicionar
  aparece desabilitado e, se o POST for forçado, recebo `ERR-CAT-002`.

**Regras de negócio**
- RN1 — Alergênicos são obrigatórios no cadastro do produto.
- RN2 — O preço exibido é o do banco, nunca parâmetro de URL.

**RNF:** RNF-USA-04, RNF-DAD-01.

---

### US-05 — Carrinho de compras

**Requerente:** Cliente · **Prioridade:** A · **Pontos:** 5 · **Telas:** TELA-005

**Ação:** Como cliente, eu quero adicionar, alterar e remover itens do carrinho, para
montar meu pedido antes de pagar.

**Critérios de aceitação**
- CA1 — DADO um produto disponível, QUANDO adiciono ao carrinho, ENTÃO a quantidade é
  somada e o subtotal é recalculado com o preço atual.
- CA2 — DADO um item no carrinho, QUANDO atualizo a quantidade para 0, ENTÃO o item é
  removido; acima do estoque, vejo `ERR-CAR-002` e a quantidade anterior é mantida.
- CA3 — DADO um item no carrinho, QUANDO clico em remover, ENTÃO ele sai e os totais
  são recalculados.
- CA4 — DADO um carrinho com itens, QUANDO qualquer página carrega, ENTÃO o contador do
  carrinho reflete a soma das quantidades.
- CA5 — DADO um carrinho vazio, QUANDO abro o carrinho, ENTÃO vejo estado vazio e o
  checkout fica bloqueado com `ERR-CAR-001`.
- CA6 — DADO que um item esgotou entre a adição e a abertura do carrinho, QUANDO a
  página carrega, ENTÃO o item é removido com aviso `ERR-CAR-003`.

**Regras de negócio**
- RN1 — O carrinho guarda apenas `produto_id → quantidade` na sessão.
- RN2 — Quantidade entre 1 e o estoque atual.
- RN3 — Preço e subtotal são sempre recalculados no servidor.
- RN4 — Carrinho não reserva estoque; a reserva ocorre no pagamento aprovado.

**RNF:** RNF-DAD-02, RNF-SEG-04.

---

## Épico C — Pedido e pagamento

### US-06 — Checkout com endereço e frete

**Requerente:** Cliente · **Prioridade:** A · **Pontos:** 8 · **Telas:** TELA-006

**Ação:** Como cliente autenticado, eu quero informar o endereço de entrega e conferir o
resumo, para transformar o carrinho em pedido.

**Critérios de aceitação**
- CA1 — DADO um visitante anônimo, QUANDO tenta abrir o checkout, ENTÃO é redirecionado
  ao login preservando o destino.
- CA2 — DADO um carrinho vazio, QUANDO abro o checkout, ENTÃO vejo `ERR-CAR-001` e não
  há criação de pedido.
- CA3 — DADO endereço e telefone válidos, QUANDO confirmo, ENTÃO o pedido é criado com
  status `recebido`, pagamento `pendente`, snapshot dos itens e do endereço, o carrinho
  é limpo e sou levado ao pagamento.
- CA4 — DADO CEP sem 8 dígitos, UF fora de 2 letras ou campo obrigatório vazio, QUANDO
  confirmo, ENTÃO vejo `ERR-CHK-002`, `ERR-CHK-003` ou `ERR-CHK-001` e nada é gravado.
- CA5 — DADO subtotal maior ou igual a R$ 120,00, QUANDO o resumo é exibido, ENTÃO o
  frete é R$ 0,00; abaixo disso, R$ 8,00.
- CA6 — DADO que o estoque mudou desde a adição, QUANDO confirmo, ENTÃO vejo
  `ERR-CAR-002` e o carrinho é ajustado.

**Regras de negócio**
- RN1 — Telefone de contato com 10 ou 11 dígitos.
- RN2 — Pedido guarda snapshot de nome, preço unitário, endereço e telefone.
- RN3 — Frete fixo de R$ 8,00, grátis a partir de R$ 120,00 (valores em configuração).
- RN4 — Nenhum preço é aceito do cliente; tudo vem do banco.
- RN5 — Criação de pedido, itens e pagamento pendente em uma única transação.

**RNF:** RNF-DAD-02, RNF-SEG-06.

---

### US-07 — Pagamento simulado

**Requerente:** Cliente · **Prioridade:** A · **Pontos:** 5 · **Telas:** TELA-007

**Ação:** Como cliente, eu quero pagar o pedido por PIX ou cartão simulado, para concluir
a compra.

**Critérios de aceitação**
- CA1 — DADO um pedido `recebido` com pagamento `pendente`, QUANDO escolho PIX e
  confirmo, ENTÃO o pagamento fica `aprovado`, o estoque é decrementado e o histórico
  registra a aprovação.
- CA2 — DADO um cartão com número que passa em Luhn e final diferente de `0000`, QUANDO
  confirmo, ENTÃO o pagamento é aprovado como no PIX.
- CA3 — DADO um cartão com final `0000`, QUANDO confirmo, ENTÃO vejo `ERR-PAG-001`,
  o pagamento fica `recusado` e posso tentar outro método.
- CA4 — DADO um número de cartão que falha em Luhn, QUANDO confirmo, ENTÃO vejo
  `ERR-PAG-002` sem qualquer tentativa de cobrança.
- CA5 — DADO um pedido já aprovado, QUANDO tento pagar de novo, ENTÃO vejo `ERR-PAG-003`.
- CA6 — DADO que o estoque ficou insuficiente, QUANDO confirmo o pagamento, ENTÃO a
  transação é desfeita e vejo `ERR-PAG-004`, sem pedido pago e sem estoque negativo.
- CA7 — DADO um pedido de outro cliente, QUANDO acesso a URL de pagamento, ENTÃO recebo
  404 com `ERR-PED-001`.

**Regras de negócio**
- RN1 — Nenhum dado completo de cartão é persistido; apenas últimos 4 dígitos e código
  de autorização simulados.
- RN2 — Decremento de estoque atômico com verificação `estoque >= quantidade`.
- RN3 — Pagamento, itens e estoque são alterados na mesma transação.

**RNF:** RNF-SEG-06, RNF-DAD-02, RNF-DAD-01.

---

### US-08 — Acompanhamento do pedido

**Requerente:** Cliente · **Prioridade:** A · **Pontos:** 5 · **Telas:** TELA-008, TELA-009

**Ação:** Como cliente, eu quero ver meus pedidos e o histórico de status, para saber o
que está acontecendo com a minha entrega.

**Critérios de aceitação**
- CA1 — DADO que tenho pedidos, QUANDO abro "Meus pedidos", ENTÃO vejo a lista com data,
  total e status, do mais recente para o mais antigo.
- CA2 — DADO um pedido meu, QUANDO abro o detalhe, ENTÃO vejo itens, endereço, pagamento
  e a linha do tempo de status.
- CA3 — DADO um pedido de outro cliente, QUANDO tento abrir o detalhe, ENTÃO recebo 404
  com `ERR-PED-001`.
- CA4 — DADO que não tenho pedidos, QUANDO abro a lista, ENTÃO vejo estado vazio com
  link para a vitrine.

**Regras de negócio**
- RN1 — Consultas sempre filtradas pelo `cliente_id` da sessão.
- RN2 — Linha do tempo ordenada por data crescente.

**RNF:** RNF-SEG-04, RNF-DES-01.

---

### US-09 — Cancelamento pelo cliente

**Requerente:** Cliente · **Prioridade:** B · **Pontos:** 3 · **Telas:** TELA-009

**Ação:** Como cliente, eu quero cancelar um pedido antes do preparo, para desistir da
compra sem prejuízo.

**Critérios de aceitação**
- CA1 — DADO um pedido `recebido`, QUANDO confirmo o cancelamento, ENTÃO o status vira
  `cancelado`, o histórico registra o autor, o estoque é reposto (se pago) e o pagamento
  fica `estornado`.
- CA2 — DADO um pedido `em_preparo`, `saiu_entrega` ou `entregue`, QUANDO tento cancelar,
  ENTÃO vejo `ERR-PED-003` e nada muda.
- CA3 — DADO o clique em cancelar, QUANDO a ação é executada, ENTÃO ela exige POST com
  CSRF válido (GET não altera estado).
- CA4 — DADO um cancelamento já efetuado, QUANDO repito a operação, ENTÃO o estoque não
  é reposto duas vezes.

**Regras de negócio**
- RN1 — Reposição de estoque idempotente.
- RN2 — Pagamento aprovado vira `estornado`; pendente vira `cancelado`.

**RNF:** RNF-DAD-02, RNF-SEG-03.

---

## Épico D — Administração

### US-10 — Administração de categorias

**Requerente:** Administrador · **Prioridade:** C · **Pontos:** 3 · **Telas:** TELA-012

**Ação:** Como administrador, eu quero manter as categorias de cupcakes, para organizar a
vitrine.

**Critérios de aceitação**
- CA1 — DADO nome inédito, QUANDO crio a categoria, ENTÃO ela é gravada com slug gerado.
- CA2 — DADO nome já existente (qualquer caixa), QUANDO crio ou renomeio, ENTÃO vejo
  `ERR-ADM-001`.
- CA3 — DADO uma categoria sem produtos, QUANDO excluo, ENTÃO ela é removida; com
  produtos, vejo `ERR-ADM-002`.
- CA4 — DADO uma categoria ativa, QUANDO a desativo, ENTÃO ela e seus produtos somem da
  vitrine e o vínculo é preservado.
- CA5 — DADO um cliente ou entregador, QUANDO acessa a rota, ENTÃO recebe 403 com
  `ERR-AUTH-007`.

**Regras de negócio**
- RN1 — Nome único case-insensitive; slug único.
- RN2 — Slug derivado do nome, sem acentos, minúsculo, hifenizado.
- RN3 — Exclusão física apenas sem produtos vinculados.

**RNF:** RNF-SEG-04, RNF-USA-04.

---

### US-11 — Administração de produtos e estoque

**Requerente:** Administrador · **Prioridade:** A · **Pontos:** 5 · **Telas:** TELA-010, TELA-011

**Ação:** Como administrador, eu quero cadastrar e editar produtos com preço e estoque,
para manter a vitrine correta.

**Critérios de aceitação**
- CA1 — DADO categoria ativa, nome, descrição, alergênicos, preço > 0 e estoque ≥ 0,
  QUANDO salvo, ENTÃO o produto aparece na vitrine se ativo.
- CA2 — DADO preço menor ou igual a zero, QUANDO salvo, ENTÃO vejo `ERR-ADM-003`; com
  estoque negativo, `ERR-ADM-004`.
- CA3 — DADO um produto existente, QUANDO altero preço ou descrição, ENTÃO a vitrine
  reflete a mudança imediatamente.
- CA4 — DADO um produto ativo, QUANDO o desativo, ENTÃO ele some da vitrine e o acesso
  direto retorna `ERR-CAT-001`.
- CA5 — DADO um produto com itens em pedidos, QUANDO tento excluir, ENTÃO vejo
  `ERR-ADM-007`; a saída é desativar.
- CA6 — DADO um usuário sem papel `admin`, QUANDO acessa, ENTÃO recebe 403.

**Regras de negócio**
- RN1 — Preço DECIMAL(10,2) > 0; estoque inteiro ≥ 0.
- RN2 — Nome e slug únicos; descrição e alergênicos obrigatórios (limites de 2000 e 255).
- RN3 — Exclusão física bloqueada por FK de itens de pedido.

**RNF:** RNF-DAD-01, RNF-SEG-06.

---

### US-12 — Gestão de pedidos e status

**Requerente:** Administrador · **Prioridade:** A · **Pontos:** 8 · **Telas:** TELA-013, TELA-014

**Ação:** Como administrador, eu quero acompanhar e mudar o status dos pedidos, para
operar a produção e a entrega.

**Critérios de aceitação**
- CA1 — DADO que existem pedidos, QUANDO abro a gestão, ENTÃO vejo a lista com filtro por
  status e identificação do cliente.
- CA2 — DADO um pedido `recebido` com pagamento `aprovado`, QUANDO mudo para
  `em_preparo`, ENTÃO o status muda e o histórico registra autor e data.
- CA3 — DADO um pedido `recebido` com pagamento `pendente` ou `recusado`, QUANDO tento
  `em_preparo`, ENTÃO vejo `ERR-PED-002`.
- CA4 — DADO um pedido `em_preparo`, QUANDO mudo para `saiu_entrega`, ENTÃO preciso
  informar um entregador ativo; sem ele, vejo `ERR-PED-002`.
- CA5 — DADO um pedido `saiu_entrega`, QUANDO mudo para `entregue`, ENTÃO o histórico é
  gravado.
- CA6 — DADO qualquer salto fora da máquina de estados, QUANDO tento, ENTÃO vejo
  `ERR-PED-002` e nada muda.
- CA7 — DADO um pedido não entregue, QUANDO o administrador cancela, ENTÃO o status vira
  `cancelado`, com reposição de estoque e estorno quando aplicável.

**Regras de negócio**
- RN1 — Transições permitidas: `recebido→em_preparo`, `em_preparo→saiu_entrega`,
  `saiu_entrega→entregue`; `cancelado` a partir de qualquer status não entregue.
- RN2 — `em_preparo` exige pagamento `aprovado`.
- RN3 — `saiu_entrega` exige `entregador_id` de usuário ativo com papel `entregador`.
- RN4 — Toda transição grava `historico_pedido` com `usuario_id`.

**RNF:** RNF-DAD-02, RNF-SEG-04.

---

### US-13 — Relatório de vendas

**Requerente:** Administrador · **Prioridade:** B · **Pontos:** 5 · **Telas:** TELA-015

**Ação:** Como administrador, eu quero um relatório de vendas por período, para acompanhar
o desempenho da loja.

**Critérios de aceitação**
- CA1 — DADO que abro o relatório sem filtro, QUANDO a página carrega, ENTÃO o período
  padrão é o dia atual.
- CA2 — DADO um período com pedidos pagos, QUANDO aplico o filtro, ENTÃO vejo quantidade
  de pedidos, receita, ticket médio e os 5 produtos mais vendidos.
- CA3 — DADO um período sem vendas, QUANDO aplico o filtro, ENTÃO todos os indicadores
  aparecem zerados, sem erro.
- CA4 — DADO um usuário sem papel `admin`, QUANDO acessa, ENTÃO recebe 403.

**Regras de negócio**
- RN1 — Receita = soma do total de pedidos com pagamento `aprovado` e status diferente de
  `cancelado` no período.
- RN2 — Ticket médio = receita ÷ número de pedidos pagos (zero quando não há pedidos).
- RN3 — Período inclusivo nas duas datas, no fuso local da loja.

**RNF:** RNF-DES-01, RNF-SEG-04.

---

## Épico E — Entrega

### US-14 — Entregas do entregador

**Requerente:** Entregador · **Prioridade:** B · **Pontos:** 5 · **Telas:** TELA-017

**Ação:** Como entregador, eu quero ver as entregas atribuídas a mim e confirmar a
conclusão, para fechar o pedido.

**Critérios de aceitação**
- CA1 — DADO que sou entregador, QUANDO abro minhas entregas, ENTÃO vejo apenas pedidos
  atribuídos a mim com status `saiu_entrega`.
- CA2 — DADO um pedido atribuído, QUANDO abro o detalhe, ENTÃO vejo endereço, telefone do
  cliente, itens e valor.
- CA3 — DADO um pedido atribuído a mim, QUANDO confirmo a entrega, ENTÃO o status vira
  `entregue` e o histórico registra o autor.
- CA4 — DADO um pedido atribuído a outro entregador, QUANDO tento confirmar, ENTÃO vejo
  `ERR-ENT-001` e nada muda.
- CA5 — DADO um usuário sem papel `entregador`, QUANDO acessa a área, ENTÃO recebe 403.

**Regras de negócio**
- RN1 — Consulta sempre filtrada por `entregador_id = sessão`.
- RN2 — Confirmação só a partir de `saiu_entrega`.
- RN3 — O entregador não altera preço, pagamento nem itens.

**RNF:** RNF-SEG-04, RNF-USA-01.

---

### US-15 — Administração de usuários

**Requerente:** Administrador · **Prioridade:** C · **Pontos:** 3 · **Telas:** TELA-016

**Ação:** Como administrador, eu quero gerenciar papéis e o estado das contas, para
controlar quem opera a loja.

**Critérios de aceitação**
- CA1 — DADO que abro a gestão, QUANDO a página carrega, ENTÃO vejo nome, e-mail, papel e
  situação de cada usuário.
- CA2 — DADO um cliente, QUANDO o promovo a entregador, ENTÃO ele passa a acessar a área
  de entregas.
- CA3 — DADO um entregador, QUANDO o reverto para cliente, ENTÃO ele perde o acesso à
  área de entregas.
- CA4 — DADO um usuário ativo, QUANDO o desativo, ENTÃO ele não consegue mais entrar;
  a desativação da própria conta é bloqueada com `ERR-ADM-005`.
- CA5 — DADO o próprio administrador, QUANDO tento rebaixar meu papel, ENTÃO a ação é
  bloqueada com `ERR-ADM-005`.
- CA6 — DADO um usuário sem papel `admin`, QUANDO acessa, ENTÃO recebe 403.

**Regras de negócio**
- RN1 — Papéis válidos: `cliente`, `entregador`, `admin`.
- RN2 — Nenhum administrador pode remover o próprio acesso.
- RN3 — Conta inativa não autentica (`ERR-AUTH-006`).

**RNF:** RNF-SEG-04, RNF-DAD-01.
