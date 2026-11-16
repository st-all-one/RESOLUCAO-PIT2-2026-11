# Template de laudo — testador externo

Preencha um arquivo por testador em `docs/07-laudo/` com o nome
`laudo-<nome>.md`. Não é necessário conhecimento técnico.

## Identificação

- Nome:
- Data e hora:
- Dispositivo e navegador (ex.: Android/Chrome, iPhone/Safari, desktop/Firefox):
- URL testada:
- Conta usada: cliente / administrador / entregador

## Roteiro (marque OK ou descreva o problema)

| # | Tarefa | Resultado |
|---|---|---|
| 1 | Criar uma conta e entrar | |
| 2 | Encontrar um cupcake pela busca | |
| 3 | Adicionar dois itens ao carrinho e alterar a quantidade | |
| 4 | Finalizar a compra com endereço válido | |
| 5 | Pagar com PIX | |
| 6 | Pagar com cartão `4242 4242 4242 4242` | |
| 7 | Tentar pagar com cartão terminado em `0000` e entender a recusa | |
| 8 | Acompanhar o pedido e cancelar enquanto estiver "Recebido" | |
| 9 | (Admin) Criar um produto e editar o preço | |
| 10 | (Admin) Avançar um pedido pago até "Saiu para entrega" | |
| 11 | (Entregador) Confirmar a entrega | |
| 12 | Usar o site apenas com teclado | |

## Perguntas abertas

1. Alguma tela ficou difícil de ler ou de tocar no celular? Onde?
2. Alguma mensagem de erro foi confusa? Qual código apareceu?
3. O que você esperava que acontecesse e não aconteceu?
4. Nota de facilidade (1 a 5):
5. Comentário livre:

## Classificação dos problemas encontrados

| Severidade | Critério |
|---|---|
| Bloqueador | Impede concluir a compra ou entrar |
| Grave | Perda de dado, valor errado ou ação impossível |
| Moderado | Confusão com contorno possível |
| Leve | Estética ou texto |

Para cada problema: tela, passos, resultado esperado, resultado obtido e, se
possível, captura de tela.
