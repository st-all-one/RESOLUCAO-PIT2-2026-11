# Histórico de revisões

Registro do ciclo de melhoria contínua (KaiZen) exigido pela Situação-Problema 1 do
PIT II. Cada linha é uma decisão com justificativa, não um log de commits.

| Versão | Data | Artefato | Mudança | Justificativa |
|---|---|---|---|---|
| 1.0 | 2026-05-25 | Especificação ágil | 15 cartões e backlog declarados em prosa no projeto de intervenção | Entrega do PIT I |
| 2.0 | 2026-11-15 | Auditoria | Constatação de que os artefatos do PIT I não foram materializados; reconstrução aprovada | Sem material não há como revisar; a auditoria registra a lacuna em vez de mascará-la |
| 2.0 | 2026-11-15 | Escopo | Serviços externos (gateway real, e-mail, app nativo) movidos para fora do escopo | Prazo e verificabilidade; o fluxo principal permanece completo |
| 2.0 | 2026-11-15 | Cartões | Critérios de aceitação reescritos em DADA/QUANDO/ENTÃO; campos RNF e prioridade A–E adicionados | O template do PIT I exige os campos e o formato é o que vira teste em P9 |
| 2.0 | 2026-11-15 | Backlog | Priorização A–E e pontos por história | Permite corte defensável se o prazo apertar |
| 2.0 | 2026-11-15 | Tarefas | Decomposição técnica com estimativa 2–12 h | Lacuna explícita do PIT I ("criar tarefas para realizar as histórias") |
| 2.0 | 2026-11-15 | Banco | Modelo físico em MariaDB 11.4 com CHECK, FK e UNIQUE | SGBD popular, exigido pelo material; integridade no banco, não só na aplicação |
| 2.0 | 2026-11-15 | Arquitetura | MVC com FastAPI + Jinja2 + TypeScript estrito | Linguagem da lista sugerida; separação explícita de models/controllers/views |
| 2.0 | 2026-11-15 | IHC | Mensagens de erro catalogadas com código, causa e ação | O material cobra telas de erro e mensagens claras |
| 2.0 | 2026-11-15 | Qualidade | ruff + mypy strict + ESLint strict-type-checked + Stylelint + sniff | Requisito do autor do projeto: tipagem forte e lint rigoroso nas duas pontas |

## Decisões que mudaram o plano original

1. **Reconstrução em vez de auditoria.** O plano pressupunha 15 cartões existentes;
   nenhum existia. A Fase P1 passou a produzir os artefatos, não apenas avaliá-los.
2. **MariaDB, não PostgreSQL.** Decisão do autor; hospedagem será escolhida entre as que
   oferecem MariaDB gerenciado.
3. **Pagamento simulado.** Mantém o fluxo e os critérios de aceitação sem criar
   dependência de conta de gateway e sem risco de armazenar dados sensíveis.
4. **Prazo comprimido.** Entrega em 2026-11-16; o cronograma de 7 semanas do plano foi
   substituído pela ordem de risco: contrato → banco → fluxo do cliente → admin →
   testes → deploy → laudos.
