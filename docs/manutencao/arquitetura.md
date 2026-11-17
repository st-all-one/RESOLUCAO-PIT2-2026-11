# Arquitetura

## Camadas

```text
Navegador
   │ HTTP (formulários, HTML)
   ▼
ContextoMiddleware ── sessão, usuário, flash, contador do carrinho
   ▼
Controllers (backend/app/controllers) ── orquestram HTTP
   ▼
Services (backend/app/services) ── regras puras e de domínio
   ▼
Models SQLAlchemy (backend/app/models) ── persistência
   ▼
MariaDB (database/schema.sql)
```

- **Controller** lê formulário, valida formato, chama serviço/modelo, grava flash
  e decide o redirect. Não contém cálculo de preço nem regra de transição.
- **Service** é testável sem HTTP. `preco`, `carrinho`, `pagamento`, `pedido`,
  `slug`, `validacao`, `endereco` e `seguranca` são funções/dataclasses sem
  dependência de request. `operacoes`, `carrinho_db` e `midia` tocam banco ou
  disco de forma controlada.
- **Model** é mapeamento e propriedades derivadas (`Pedido.total`,
  `ItemPedido.subtotal`). Nada de acesso a sessão HTTP.
- **Template** só formata dados recebidos; sem consulta ao banco.

## Ciclo de uma requisição

1. `ContextoMiddleware` lê o cookie de sessão, carrega o usuário ativo, consome o
   flash e conta os itens do carrinho.
2. A dependência `validar_csrf` roda nos routers que aceitam mutação e compara o
   campo `csrf_token` com o token da sessão.
3. A dependência de acesso (`exigir_usuario` ou `exigir_papel`) resolve o ator.
4. O controller executa e responde:
   - `renderizar` → HTML 200;
   - `renderizar_form` → HTML com erro e status do catálogo (422/409/…);
   - `redirecionar` → 303 com flash.
5. Exceções de domínio (`ErroAplicacao`) são convertidas pelo handler global em
   Problem Details RFC 9457 (JSON ou HTML, conforme `Accept`).

## Fronteiras importantes

| Fronteira | Regra |
|---|---|
| HTTP ↔ domínio | Controller não calcula dinheiro; serviço não lê `Request` |
| Domínio ↔ banco | Serviço recebe `Session`; nunca abre conexão própria |
| Template ↔ banco | Proibido consultar banco no Jinja |
| Frontend ↔ backend | Contrato são rotas, nomes de campo e códigos de erro |
| Sessão ↔ banco | Carrinho vive na sessão e é preservado ao autenticar; pedido persistido é a fonte de verdade |

## Estáticos

O CSS e o TypeScript têm fonte em `frontend/` e são publicados em
`backend/app/static/`:

```text
frontend/src/app.ts ──tsc──▶ backend/app/static/js/app.js
frontend/src/estilo.css ──cópia──▶ backend/app/static/css/estilo.css
```

O build é `npm --prefix frontend run build` (`make front-build`). Em
desenvolvimento, rode-o após alterar TS/CSS. A imagem Docker faz o build no stage
`frontend` e copia o resultado para o runtime.

## Imagens enviadas

Imagens de produto enviadas pelo admin não entram no pacote estático: ficam em
`settings.diretorio_midias` (padrão `uploads/`, `/app/uploads` no container) e são
servidas em `/midia`. O volume `cupcake-uploads` preserva os arquivos entre
builds; o banco guarda apenas o caminho (`/static/...` ou `/midia/...`).

## Onde a consistência é garantida

- **Preço**: `services/preco.py` e propriedades dos modelos.
- **Estoque**: `UPDATE ... WHERE estoque >= quantidade` dentro da transação de
  pagamento; rollback em caso de `rowcount != 1`.
- **Status**: `services/pedido.py` centraliza a máquina de estados.
- **Cancelamento**: `services/operacoes.py` estorna pagamento e estoque.
- **Autorização**: `core/acesso.py` + filtros por `cliente_id`/`entregador_id`.

Diagramas detalhados: [../03-uml/diagramas.md](../03-uml/diagramas.md).
