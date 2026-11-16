# Auditoria da documentação do PIT I

**Data:** 2026-11-15
**Fonte primária disponível:** `2026_05_25_STALLONE_LOPES_DE_SOUZA_34648658.pdf` (3 páginas)
**Método:** confronto entre o que o material do PIT I exige e o que existe fisicamente no acervo.

## Resultado

O PDF de intervenção **declara** a execução de 15 cartões, mapa de afinidade, backlog
priorizado e estimativas em horas, mas **não contém** nenhum desses artefatos: ele descreve
o procedimento em prosa. A varredura do ambiente (`~/projects`) não encontrou repositório,
planilha, exportação de Trello, diagrama ou wireframe do PIT I.

Consequência: a Fase P1 do plano não é uma auditoria de material existente, e sim uma
**reconstrução versionada** a partir do briefing de negócio. Todo artefato abaixo nasce
aqui com status explícito e histórico em `historico-revisoes.md`.

## Entregáveis do PIT I

| # | Entregável exigido no PIT I | Situação no acervo | Evidência | Ação no PIT II |
|---|---|---|---|---|
| 1 | Escopo/ideia do produto | Parcial | PDF, p. 1–3 (prosa) | Formalizado em `escopo-revisado.md` |
| 2 | Personas (Cliente, Administrador, Entregador) | Parcial | PDF, p. 2 | Reafirmadas nos cartões |
| 3 | Mínimo de 15 cartões de história | Ausente | PDF declara, conteúdo não existe | Reconstruídos em `02-especificacao/cartoes.md` |
| 4 | Template completo do cartão (ID, título, requerente, ação, comentários, CA, RN, RNF, prioridade, pontos) | Ausente | — | Template T1 aplicado nos 15 cartões |
| 5 | Mapa de afinidade | Ausente | PDF cita "eixos temáticos" | `02-especificacao/mapa-afinidade.md` |
| 6 | Product Backlog priorizado | Ausente | PDF cita Trello, sem exportação | `02-especificacao/backlog.md` |
| 7 | Tarefas técnicas derivadas das histórias, 2–12 h | Ausente | — | `02-especificacao/tarefas.md` |
| 8 | Caso de uso geral | Ausente | — | `03-uml/casos-de-uso.md` |
| 9 | Casos de uso expandidos | Ausente | — | `03-uml/casos-de-uso-expandidos.md` |
| 10 | Diagrama de classes de persistência | Ausente | — | `03-uml/classes.md` |
| 11 | Diagrama de sequência | Ausente | — | `03-uml/sequencia.md` |
| 12 | Diagrama de atividades | Ausente | — | `03-uml/atividades.md` |
| 13 | Wireframes | Ausente | — | `04-ihc/wireframes.md` |
| 14 | Mockups de média/alta fidelidade | Ausente | — | Implementados na própria interface (P8) |
| 15 | Mapa conceitual e navegacional | Ausente | — | `04-ihc/mapas.md` |
| 16 | Catálogo de mensagens de erro | Ausente | — | `04-ihc/mensagens-erro.md` |
| 17 | Projeto conceitual e lógico normalizado | Ausente | — | `05-dados/conceitual.md`, `05-dados/logico.md` |
| 18 | Projeto físico + dicionário de dados | Ausente | — | `db/schema.sql`, `05-dados/dicionario.md` |

## Riscos herdados

| Risco | Efeito | Mitigação |
|---|---|---|
| Documentação declarada mas inexistente | Retrabalho de 6–8 h na reconstrução | Reconstrução feita uma vez, versionada e rastreável |
| Backlog sem tarefas (lacuna típica do PIT I) | Sprint sem decomposição | Toda história tem ≥ 3 tarefas entre 2 e 12 h |
| Critérios de aceitação em prosa | Teste não verificável | Conversão integral para DADA/QUANDO/ENTÃO |

## Decisão

Aprovar a reconstrução como **versão 2.0** da documentação de planejamento, registrando
no histórico o que mudou e por quê. O escopo é congelado no gate G1.
