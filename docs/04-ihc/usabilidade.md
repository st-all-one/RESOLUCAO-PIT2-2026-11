# Usabilidade e IHC — decisões e evidências

## Público e contexto

- **Cliente**: compra pelo celular, muitas vezes em rede móvel; precisa de busca
  rápida, preço visível e checkout curto.
- **Administrador**: opera em desktop, com teclado, em sessões curtas de gestão.
- **Entregador**: usa o celular na rua; precisa de endereço, telefone clicável e
  confirmação em um toque.

## Decisões de interação

| Decisão | Motivo |
|---|---|
| Mobile-first (coluna única até 48 rem) | Maior parte do tráfego é celular |
| Busca e filtro na própria vitrine | Evita página intermediária e reduz toques |
| Quantidade editável no carrinho | Corrige o pedido sem remover e readicionar |
| Frete e total recalculados no servidor | Impede divergência entre tela e cobrança |
| PIX como opção padrão | Aprovação imediata na simulação, menos fricção |
| Cartão com máscara e dica de teste | Reduz erro de digitação sem esconder a regra |
| Mensagens com código (`ERR-...`) | Facilita suporte e registro no laudo |
| Confirmação antes de excluir/cancelar | Prevenção de erro (heurística de Nielsen) |
| Foco visível e link "Pular para o conteúdo" | Navegação por teclado |
| Estados vazios com ação | Evita becos sem saída |

## Heurísticas de Nielsen

1. **Visibilidade do estado**: selos de status, contador do carrinho, linha do
   tempo do pedido.
2. **Linguagem do usuário**: textos em português, valores em real, códigos
   internos apenas como apoio.
3. **Controle e liberdade**: cancelamento de pedido e remoção de item.
4. **Consistência**: mesmo padrão de cartão, botão e mensagem em todas as telas.
5. **Prevenção de erro**: validação de CEP, UF, telefone, estoque e Luhn antes
   de persistir; confirmação em ações destrutivas.
6. **Reconhecimento**: categorias e busca visíveis; endereço anterior pré-preenchido.
7. **Eficiência**: poucos passos entre vitrine e pagamento.
8. **Estética minimalista**: uma ação primária por tela.
9. **Recuperação de erro**: mensagem com campo e instrução, sem perder os dados.
10. **Ajuda**: dicas de formato junto aos campos e contas de demonstração no README.

## Evidências

- Auditoria `sniff` com contraste AA aprovado, foco e alvos sem falhas.
- Testes automatizados cobrem os fluxos que sustentam as mensagens (43 casos).
- Roteiro com 12 tarefas para testadores externos em
  `docs/07-laudo/template-laudo-testador.md`.

## Pendências de validação

- Cinco testadores externos ainda não recrutados; o template está pronto.
- AAA de contraste não é meta; caso o público solicite, escurecer a primária.
