# Ciclo de feedback dos testadores (2026-11-16/17)

Consolidação dos cinco laudos recebidos após o teste guiado em
<https://cupcake.dvmax.stream>. Cada relato foi classificado e virou uma fatia
funcional com teste de regressão. O que funcionou foi preservado; o que falhou
foi corrigido; o que faltava foi implementado.

## Relatos

| Data/hora | Testador | Funcionou | Falhou | Faltou / não implementado |
|---|---|---|---|---|
| 16/11 21:31 | Matheus Alves Teodoro | Consulta automática de endereço via API de CEP | Carrinho é esvaziado ao entrar na conta para concluir a compra | Edição de dados cadastrais depois do cadastro |
| 17/11 08:11 | Heloísa Felizardo Campos | Carrinho, cadastro, login, checkout, CEP, pedido pago, consulta e cancelamento | Admin não permite adicionar imagem ao editar/criar item | Cadastro de novos itens pelo admin |
| 17/11 08:15 | Amanda Maia | Carrinho, login, CEP, detalhe do produto, alergênicos | Ao trocar de conta o checkout mostrava endereço/telefone de outra conta sem perguntar qual usar | Reativar produto excluído; excluir apagava tudo |
| 17/11 08:17 | Rodivan Pereira Ramos | Admin atualiza estoque, desativa e reativa item | Administração de itens ruim no mobile; não conseguiu trocar a imagem de um produto | — |
| 17/11 08:19 | Priscilla Pavan Ladeia da Silva | Telas, menus, carrinho, pagamento, endereço | Tela de endereço com overflow lateral no mobile | Não encontrou como testar a visão do entregador |

## O que foi feito

### 1. Carrinho preservado ao autenticar (Matheus)

`controllers/auth.py` passou a guardar o carrinho da sessão antes de regenerar a
sessão no login/cadastro e a regravá-lo depois (`_iniciar_sessao`). O visitante
que monta o carrinho e entra para pagar continua com os itens.

- Testes: `test_auth.py::test_login_preserva_carrinho_montado_como_visitante`,
  `::test_cadastro_preserva_carrinho_montado_como_visitante`.
- A regeneração da sessão e a proteção CSRF continuam iguais.

### 2. Edição de dados cadastrais (Matheus)

Nova área `/conta` (`controllers/conta.py` e `templates/conta/index.html`) com:

- alteração de nome, e-mail e telefone, com unicidade de e-mail;
- troca de senha exigindo a senha atual; as outras sessões são invalidadas
  (`sessao_versao`) e a sessão atual continua válida;
- gestão de endereços: adicionar com CEP automático, definir principal e remover.

- Testes: `test_conta.py` (6 cenários).

### 3. Endereço explícito no checkout (Amanda)

O checkout não escolhe mais um endereço escondido. Quando existem endereços
salvos, a tela mostra a lista da conta e um rádio **Outro endereço**; o endereço
principal vem selecionado, mas o usuário vê exatamente qual será usado. O bloco
de campos só aparece para “Outro endereço” (com JS; sem JS o servidor ainda
respeita o rádio escolhido). O telefone aparece como “da conta”, separado do
endereço, e pode ser corrigido no pedido ou em `/conta`.

O servidor valida que `endereco_id` pertence ao usuário autenticado; um id de
outra conta é recusado com `ERR-CHK-001`.

- Testes: `test_compra.py::test_checkout_oferece_endereco_salvo_e_usa_o_escolhido`,
  `::test_checkout_nao_aceita_endereco_de_outra_conta`.
- O preenchimento automático do navegador (autofill do dispositivo) não é mais a
  única fonte visual: o endereço da conta é exibido por extenso.

### 4. Imagem de produto no admin (Heloísa e Rodivan)

O formulário de produto aceita JPG, PNG ou WebP de até 2 MB, mostra a prévia da
imagem atual e permite trocar ou remover. O conteúdo é validado pela assinatura
do arquivo (não pelo `Content-Type`), recebe nome aleatório em `services/midia.py`
e é servido em `/midia`. A imagem antiga enviada é apagada ao trocar.

- Volume `cupcake-uploads` em `/app/uploads` no `compose.yaml`.
- Testes: `test_admin.py::test_admin_cria_e_troca_imagem_do_produto`,
  `::test_admin_rejeita_arquivo_que_nao_e_imagem`.
- Erro novo: `ERR-ADM-010`.

### 5. Exclusão com restauração (Amanda)

Excluir produto não apaga mais a linha: grava `produtos.excluido_em`, tira da
vitrine/carrinho e move para **Lixeira** no admin. A lixeira lista os produtos e
oferece **Restaurar**, que devolve o item (ativo se houver estoque) mantendo
histórico de pedidos e imagem.

- Migração: `database/migracoes/2026-11-17-exclusao-logica-produto.sql`.
- Teste: `test_admin.py::test_exclusao_logica_preserva_produto_e_restaura`.
- `ERR-ADM-007` foi removido: nenhuma exclusão é bloqueada por histórico.

### 6. Admin no mobile (Rodivan)

Listas de produtos e pedidos viram cartões no mobile (`.tabela-cartoes`), com
rótulo por campo e botões de ação em linha com alvo mínimo de 44 px. O produto
mostra miniatura, situação e acesso direto a **Editar**.

### 7. Overflow lateral do checkout (Priscilla)

A causa era o item de grid com `min-width: auto`: a tabela de resumo definia a
largura mínima da coluna e esticava a página para 423 px em um viewport de 390 px.
`.grade > * { min-width: 0 }` deixou a tabela rolar dentro do próprio
`.tabela-responsiva` (390 px, medido no navegador antes e depois).

### 8. Visão do entregador (Priscilla)

A tela de login agora traz um bloco “Contas de demonstração” com os três papéis e
explica que `/entregas` mostra os pedidos atribuídos ao entregador. A lista vazia
também ensina o caminho: o admin marca “Saiu para entrega” e escolhe o entregador.

## Validação final

- `make check`: ruff, formatação, mypy strict, ESLint, Stylelint e pytest verdes.
- Navegador real em viewport 390×844: checkout sem overflow lateral; upload,
  troca de imagem, exclusão/restauração e troca de endereço exercitados pela UI.
- Deploy: <https://cupcake.dvmax.stream> (stack `cupcake-gourmet`, porta 23020).
