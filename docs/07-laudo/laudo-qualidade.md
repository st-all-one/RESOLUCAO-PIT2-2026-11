# Laudo de qualidade — Cupcake Gourmet 2.0

Data da execução: 2026-11-15. Ambiente: Linux, Python 3.15, Node 22,
MariaDB 11.4 em Docker, Chromium via sniff 0.5.1.

## Ferramentas e resultado

| Ferramenta | Comando | Resultado |
|---|---|---|
| ruff (lint) | `ruff check .` | 0 erros |
| ruff (formato) | `ruff format --check .` | 45 arquivos formatados |
| mypy strict | `mypy src tests scripts` | 0 erros em 45 arquivos |
| ESLint strict-type-checked | `npm run lint` | 0 erros |
| Stylelint | incluído em `npm run lint` | 0 erros |
| pytest | `pytest` | **43 aprovados** |
| Cobertura | `pytest --cov=app` | **83%** (1352 linhas) |
| sniff | `sniff capture` + `sniff check` | WCAG AA sem falhas |

## Acessibilidade (sniff)

Capturas em `artifacts/sniff-home.jsonl` e `artifacts/sniff-cadastro.jsonl`,
com `--depth 8` para incluir a árvore da página.

- **Home**: 146 verificações, 102 aprovadas e 44 falhas — todas de contraste
  **AAA** (7:1). Nenhuma falha AA (4,5:1). Menor razão observada: 6,08:1.
- **Cadastro**: 40 verificações, 25 aprovadas, 11 falhas AAA e 4 avisos.
- Os 4 avisos `control-without-name` são **falso positivo**: os campos possuem
  `<label for="...">`; o sniff não resolve a associação `for` no recorte.
- Alvos de toque, foco visível, `alt` e uniformidade: sem falhas.
- Conclusão: **WCAG 2.1 nível AA atendido**; AAA não é requisito do projeto e
  exigiria escurecer a paleta primária.

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
| AAA de contraste não atendido | Requisito é AA; paleta pode ser escurecida se necessário |
| Testadores externos não recrutados | Template em `docs/07-laudo/template-laudo-testador.md` |

## Parecer

A solução atende aos requisitos funcionais das 15 histórias e aos requisitos não
funcionais de segurança, consistência de estoque, acessibilidade AA e qualidade
estática. Está apta à validação com usuários e ao deploy, condicionada à
configuração do provedor.
