# Dívidas técnicas e próximos passos

Itens conhecidos, com impacto e sugestão. Nenhum bloqueia a entrega.

| Item | Impacto | Sugestão |
|---|---|---|
| Cobertura de `controllers/admin.py` em 54% | ramos de erro pouco exercitados | testes de exclusão protegida, duplicidade e validação de formulário |
| Sem migrações versionadas | alterações de schema são manuais | adotar Alembic ou script incremental com histórico |
| Sem teste E2E de navegador | regressões visuais dependem de sniff/manual | Playwright cobrindo compra e admin |
| Pagamento simulado | não há integração real | adaptar `services/pagamento.py` a um gateway |
| Carrinho só na sessão | não persiste entre dispositivos | mover para tabela `carrinhos` se virar requisito |
| Sem rate limit/login lockout | força bruta possível | limitar tentativas por IP/e-mail no proxy ou app |
| Sem e-mail transacional | status só é visto no site | integrar provedor e templates |
| `SESSION_COOKIE_SECURE` manual | erro de configuração em HTTPS | inferir de `APP_BASE_URL` ou falhar no startup |
| Sem observabilidade | diagnóstico depende de logs | métricas e tracing (OpenTelemetry) |
| Sem CI | `make check` é local | GitHub Actions rodando lint, tipos e testes |

## Dicas de evolução

- Mantenha o catálogo de erros como contrato; consumidores e testes dependem dele.
- Preserve a baixa condicional de estoque ao refatorar o pagamento.
- Ao adicionar papel novo, atualize `core/acesso.py`, navegação e testes.
- Ao mexer em datas, lembre que o banco está em UTC e a apresentação em
  America/Sao_Paulo.
