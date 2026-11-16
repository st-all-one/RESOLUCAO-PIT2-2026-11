# Decisões de arquitetura (ADRs resumidos)

## ADR-01 — FastAPI com Jinja2, sem SPA

**Contexto**: entrega acadêmica, prazo curto, foco em fluxo completo e
acessibilidade. **Decisão**: renderização no servidor com Jinja2; TypeScript
apenas para melhorias progressivas. **Consequências**: menos build, SEO e
acessibilidade melhores, menos estado no cliente; interações ricas exigem
recarregar a página.

## ADR-02 — MariaDB com SQLAlchemy síncrono

**Contexto**: o enunciado pede MySQL e o ambiente já tinha Docker. **Decisão**:
MariaDB 11.4, PyMySQL e SQLAlchemy 2 síncrono. **Consequências**: transações
simples de raciocinar, sem async complexo; a suíte usa o mesmo banco da produção.

## ADR-03 — Pagamento simulado

**Contexto**: não há gateway real no escopo. **Decisão**: PIX aprova sempre;
cartão valida Luhn e recusa final `0000`; nenhum dado completo é armazenado.
**Consequências**: fluxo demonstrável e testável; trocar por gateway real exige
novo serviço atrás da mesma interface (`simular`).

## ADR-04 — Carrinho na sessão, pedido no banco

**Contexto**: o carrinho é temporário e não precisa de histórico. **Decisão**:
`dict` na sessão, reconciliado com o banco em `carrinho_db`; ao fechar o pedido,
preços e nomes viram snapshot. **Consequências**: menos tabelas e escrita;
carrinhos não sobrevivem à troca de navegador e preços são revalidados no
checkout.

## ADR-05 — Estático construído para o backend

**Contexto**: o backend serve templates e estáticos; o front precisa de TypeScript
estrito e CSS com lint. **Decisão**: fontes em `frontend/`, build publica em
`backend/app/static/`; Docker executa o build no stage `frontend`.
**Consequências**: um único diretório servido, sem bundler; é preciso rodar
`make front-build` após alterar TS/CSS em desenvolvimento.

## ADR-06 — Testes de integração com MySQL real

**Contexto**: estoque, CHECKs e transações são o núcleo do risco. **Decisão**:
pytest contra `cupcake_test`, schema recriado e tabelas truncadas por teste.
**Consequências**: confiança alta no comportamento real; a suíte exige Docker e é
mais lenta que testes unitários puros.

## ADR-07 — Problem Details RFC 9457 com código de domínio

**Contexto**: erros precisam ser legíveis para usuário e rastreáveis em teste.
**Decisão**: catálogo `ERR-*`, status HTTP próprio e corpo JSON padronizado, com
negociação HTML/JSON. **Consequências**: contrato estável e testável; todo erro
novo precisa de código e documentação.
