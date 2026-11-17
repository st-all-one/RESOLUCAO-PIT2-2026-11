# Laudo de qualidade — Cupcake Gourmet 2.0

Data da execução: 2026-11-17 (após o ciclo de feedback dos testadores). Ambiente: Linux, Python 3.15, Node 22,
MariaDB 11.4 em Docker, Chromium via sniff 0.5.1.

## Ferramentas e resultado

| Ferramenta | Comando | Resultado |
|---|---|---|
| ruff (lint) | `ruff check .` | 0 erros |
| ruff (formato) | `ruff format --check .` | 79 arquivos formatados |
| mypy strict | `mypy backend/app tests backend/scripts` | 0 erros em 54 arquivos |
| ESLint strict-type-checked | `npm run lint` | 0 erros |
| Stylelint | incluído em `npm run lint` | 0 erros |
| pytest | `pytest` | **88 aprovados** |
| Cobertura | `pytest --cov=app` | **88%** (1809 linhas) |
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

- Mobile-first: layout de coluna única até 48 rem, grade fluida acima; no mobile a
  navegação vira um menu hambúrguer acessível e o rodapé fixo mostra o nome do projeto.
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
| Deploy público | <https://cupcake.dvmax.stream> com HTTPS e health check |
| Cobertura de `admin.py` em 69% | Fluxos principais e upload/lixeira testados; ramos de erro no roteiro manual |
| Contraste AAA | Paleta escurecida; menor razão 7,04:1 |
| Feedback de testadores | Cinco laudos consolidados em `docs/07-laudo/feedback-testadores.md` |
| Overflow mobile | Corrigido e medido em viewport 390×844; `scrollWidth == clientWidth` |

## Parecer

A solução atende aos requisitos funcionais das 19 histórias (15 planejadas + 4
abertas no ciclo de feedback) e aos requisitos não funcionais de segurança,
consistência de estoque, acessibilidade AA/AAA de contraste e qualidade estática.
Os cinco laudos foram endereçados e publicados em
<https://cupcake.dvmax.stream>.
