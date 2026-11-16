# Escopo revisado — Cupcake Gourmet 2.0

## Problema

A loja de cupcakes gourmet teve uma tentativa anterior de sistema fracassada por
elicitação imprecisa: requisitos ambíguos geraram retrabalho e prejuízo à marca. O
produto precisa de uma especificação sem ambiguidade e de um sistema que execute o
fluxo de venda ponta a ponta — vitrine, carrinho, pagamento, preparo e entrega — com
regras de negócio verificáveis.

## Público

| Ator | Necessidade central |
|---|---|
| Cliente | Encontrar cupcakes, montar o pedido, pagar e acompanhar a entrega |
| Administrador | Manter catálogo, operar pedidos, acompanhar vendas e usuários |
| Entregador | Receber as entregas atribuídas e confirmar a conclusão |

## Dentro do escopo

1. Cadastro, login e logout de clientes com sessão segura.
2. Vitrine com busca textual, filtro por categoria e indicação de esgotado.
3. Detalhe do produto com preço, descrição e alergênicos.
4. Carrinho em sessão com validação de estoque e recálculo de preço no servidor.
5. Checkout com endereço validado, frete por regra e snapshot do pedido.
6. Pagamento **simulado** (PIX aprovado; cartão com validação de Luhn e recusa
   determinística para final `0000`), sem armazenar dados de cartão.
7. Acompanhamento do pedido por cliente e cancelamento antes do preparo.
8. Administração de categorias, produtos, pedidos, usuários e relatório de vendas.
9. Área do entregador com confirmação de entrega.
10. Testes automatizados, lint rigoroso, health check e deploy público.

## Fora do escopo (congelado)

| Item | Motivo |
|---|---|
| Gateway de pagamento real | Exige contrato, credenciais e tratamento de webhooks; simulação cobre o fluxo e os critérios de aceitação |
| Envio de e-mail (confirmação, recuperação de senha) | Dependência externa sem impacto no fluxo principal |
| Aplicativo nativo iOS/Android | Aplicação web mobile-first atende "web ou mobile" |
| Cupons, fidelidade e avaliações | Não constam do briefing de negócio |
| Geolocalização e cálculo de rota | Frete por faixa fixa é suficiente e verificável |
| Multiloja e internacionalização | Fora do modelo de negócio da marca |
| Integração com estoque externo | Estoque é mantido no próprio banco |

## Critérios de sucesso

- Os 15 cartões implementados e rastreados até teste automatizado.
- `make check` verde (ruff, mypy strict, ESLint, Stylelint, pytest).
- URL pública executando o fluxo completo com o `seed.sql`.
- Nenhum segredo versionado; nenhuma stack trace exposta ao usuário.
- Cinco laudos reais coletados com evidência e laudo de qualidade fechado.

## Congelamento

Escopo congelado em 2026-11-15 (gate G1). Qualquer inclusão exige justificativa em
`historico-revisoes.md` e reavaliação de prazo.
