# Convenções

## Idioma e nomes

- Código, rotas, mensagens, commits e documentação em **português brasileiro**.
- Classes em PascalCase (`Pedido`, `ErroAplicacao`); funções, variáveis e campos
  em snake_case (`calcular_frete`, `produto_id`).
- Tabelas e colunas no singular (`pedidos`, `itens_pedido`).
- Rotas em kebab-case quando composta (`/admin/pedidos`, `/entregas`).
- Códigos de erro no formato `ERR-ÁREA-NNN` (`ERR-PAG-001`).

## Commits

Formato convencional, sempre em português:

```text
tipo(escopo): resumo no imperativo

- motivo e decisões relevantes
```

Tipos usados: `feat`, `fix`, `docs`, `test`, `style`, `chore`, `build`.
Commits pequenos e por fatia funcional; não misture refatoração com feature.

## Back-end

- `ruff` com linha de 100 e `mypy --strict`.
- Controller não calcula dinheiro nem transita status; use serviços.
- Toda mutação por formulário declara `Depends(validar_csrf)` no router.
- Toda página autenticada usa `exigir_usuario`/`exigir_papel`.
- Erros de domínio apenas via `ErroAplicacao`; nunca `HTTPException` crua.
- Dinheiro em `Decimal`; nunca `float`.
- Datas do banco são UTC; conversão de fuso só na borda de apresentação.
- Consultas que podem concorrer usam `with_for_update()` ou `UPDATE` condicional.

## Templates e front-end

- Mobile-first; uma ação primária por tela.
- Todo campo tem `<label for="...">`.
- Mensagens de erro com código visível e `role="alert"`.
- Tabelas em `.tabela-responsiva`.
- CSS com classes BEM-like (`bloco__elemento--modificador`) e variáveis em
  `:root`.
- TypeScript estrito: sem `any`, sem `console`, funções com tipo de retorno.
- Comportamento sem JS deve continuar funcionando (melhoria progressiva).
- Contraste mínimo AA; o alvo atual é AAA (7:1).

## Testes

- Integração contra MariaDB real (`cupcake_test`), nunca SQLite.
- Um cenário por teste; use as fixtures `dados` e `cliente_http`.
- Verifique efeito no banco (`escalar`), não só o HTML.
- Não teste detalhe de implementação; teste contrato visível.
- Toda correção de bug ganha teste que falharia antes.

## Checklist de revisão

- [ ] `make check` verde.
- [ ] Rota nova registrada e coberta.
- [ ] CSRF e autorização presentes.
- [ ] Erro novo no catálogo e na documentação.
- [ ] Estoque/preço/isolamento preservados.
- [ ] Template acessível e responsivo.
- [ ] Docs e dicionário atualizados quando o schema muda.
- [ ] Commit em português, escopo coerente.
