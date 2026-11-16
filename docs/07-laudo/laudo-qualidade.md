# Laudo de qualidade — Cupcake Gourmet 2.0

Data da execução: 2026-11-16. Ambiente: Linux, Python 3.15, Node 22,
MariaDB 11.4 em Docker, Chromium via sniff 0.5.1.

## Ferramentas e resultado

| Ferramenta | Comando | Resultado |
|---|---|---|
| ruff (lint) | `ruff check .` | 0 erros |
| ruff (formato) | `ruff format --check .` | 79 arquivos formatados |
| mypy strict | `mypy src tests scripts` | 0 erros em 50 arquivos |
| ESLint strict-type-checked | `npm run lint` | 0 erros |
| Stylelint | incluído em `npm run lint` | 0 erros |
| pytest | `pytest` | **76 aprovados** |
| Cobertura | `pytest --cov=app` | **86%** (1557 linhas) |
| sniff | `sniff capture` + `sniff check` | 0 falhas; contraste AAA |

## Acessibilidade (sniff)

Capturas em `artifacts/sniff-home.jsonl` e `artifacts/sniff-cadastro.jsonl`,
com `--depth 8` para incluir a árvore da página.

- **Home**: 146 verificações, **146 aprovadas, 0 falhas**.
- **Cadastro**: 40 verificações, 36 aprovadas, 0 falhas e 4 avisos.
- Os 4 avisos `control-without-name` são **falso positivo**: os campos possuem
  `<label for="...">`; o sniff não resolve a associação `for` no recorte.
- Alvos de toque, foco visível, `alt` e uniformidade: sem falhas.
- Contraste mínimo após ajuste da paleta: **7,04:1** (AAA exige 7:1 para texto
  normal).
- Conclusão: **WCAG 2.1 níveis AA e AAA de contraste atendidos**.

## Usabilidade e IHC

- Mobile-first: layout de coluna única até 48 rem, grade fluida acima.
- Pular para o conteúdo, foco visível, `aria-label` no contador do carrinho,
  `aria-current` no filtro de pedidos, mensagens com `role="alert"/"status"`.
- Confirmação antes de ações destrutivas; sem JavaScript o formulário ainda
  funciona (a confirmação é uma melhoria progressiva).
- Erros sempre com código, campo e instrução de correção; ver
  `docs/04-ihc/mensagens-erro.md`.

## Segurança

- Senhas com scrypt e salt; nenhum dado completo de cartão é persistido.
- CSRF obrigatório em POST/PUT/PATCH/DELETE (token de sessão comparado com
  `compare_digest`).
- Autorização por papel em `/admin` e `/entregas`; pedidos e entregas isolados
  por usuário.
- Estoque baixado com `UPDATE ... WHERE estoque >= quantidade` para evitar
  corrida; transação revertida quando insuficiente.
- Cookies `HttpOnly` e `SameSite=Lax`; `Secure` configurável por ambiente.

## Riscos e pendências

| Risco | Mitigação atual |
|---|---|
| Deploy público ainda não realizado | Dockerfile multi-stage pronto; provedor com MariaDB a definir |
| Cobertura de `admin.py` em 54% | Fluxos principais testados; ramos de erro no roteiro manual |
| Contraste AAA | Paleta escurecida; menor razão 7,04:1 |
| Testadores externos não recrutados | Template em `docs/07-laudo/template-laudo-testador.md` |

## Parecer

A solução atende aos requisitos funcionais das 15 histórias e aos requisitos não
funcionais de segurança, consistência de estoque, acessibilidade AA/AAA de
contraste e qualidade estática. Está apta à validação com usuários e ao deploy, condicionada à
configuração do provedor.
