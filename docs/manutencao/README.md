# Manutenção do projeto

Documentação para quem vai evoluir o Cupcake Gourmet depois da entrega. O
objetivo é responder rápido a três perguntas: **onde fica**, **como alterar** e
**como verificar**.

## Por onde começar

| Preciso… | Leia |
|---|---|
| Entender as camadas e o ciclo de uma requisição | [arquitetura.md](arquitetura.md) |
| Saber qual arquivo alterar | [mapa-codigo.md](mapa-codigo.md) |
| Rodar, depurar e criar uma feature | [desenvolvimento.md](desenvolvimento.md) |
| Seguir os padrões do projeto | [convencoes.md](convencoes.md) |
| Publicar, atualizar, backup e incidentes | [operacao.md](operacao.md) |
| Entender decisões e alternativas descartadas | [decisoes.md](decisoes.md) |
| Ver o que ainda pode melhorar | [dividas-tecnicas.md](dividas-tecnicas.md) |

## Visão de 30 segundos

```text
frontend/  ── compila TS + copia CSS ──▶ backend/app/static/
backend/   ── FastAPI + Jinja2 + SQLAlchemy ──▶ MariaDB (database/)
tests/     ── pytest de integração contra cupcake_test
docs/      ── produto, engenharia e operação
```

O navegador recebe HTML renderizado no servidor. O JavaScript é uma melhoria
progressiva: toda jornada funciona sem ele.

## Contratos que não podem quebrar

1. **Códigos de erro** (`ERR-*`) são API pública: aparecem na tela, nos testes e
   na documentação. Nunca reutilize um código para outro significado.
2. **CSRF** é obrigatório em toda mutação por formulário.
3. **Estoque** só é baixado na aprovação do pagamento, de forma condicional.
4. **Preço do pedido** é snapshot (`itens_pedido.preco_unitario`); mudar o
   produto não altera pedidos antigos.
5. **Isolamento**: cliente só vê os próprios pedidos; entregador só as próprias
   entregas.
6. `make check` precisa continuar verde: ruff, mypy, ESLint, Stylelint, tsc e
   pytest.

## Mapa da documentação

```text
docs/
├── 01-planejamento/     auditoria do PIT I, escopo, histórico
├── 02-especificacao/    histórias, backlog, RNF, rastreabilidade
├── 03-uml/              casos de uso, classes, estados, sequência
├── 04-ihc/              usabilidade e catálogo de mensagens
├── 05-dados/            conceitual, lógico e dicionário gerado
├── 06-testes/           estratégia e relatório da suíte
├── 07-laudo/            laudo de qualidade e template dos testadores
├── 08-deploy/           guia da VPS com Docker
├── manutencao/          este conjunto
└── manual-de-uso.md     roteiro dos três papéis
```
