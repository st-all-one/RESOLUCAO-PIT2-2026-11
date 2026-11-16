# Deploy — Cupcake Gourmet 2.0

## Requisitos

- Imagem com o `Dockerfile` da raiz (multi-stage: Node compila o TypeScript,
  Python instala o pacote e serve a aplicação).
- MariaDB 11.4 (ou MySQL 8 compatível) acessível pela aplicação.
- Variáveis de ambiente:

| Variável | Obrigatória | Exemplo |
|---|---|---|
| `APP_SECRET` | sim | chave aleatória de 32+ bytes |
| `DATABASE_URL` | sim | `mariadb+pymysql://usuario:senha@host:3306/banco?charset=utf8mb4` |
| `APP_ENV` | recomendada | `production` |
| `APP_BASE_URL` | recomendada | `https://cupcake.exemplo.com` |
| `SESSION_COOKIE_SECURE` | sim em HTTPS | `true` |
| `FRETE_VALOR` / `FRETE_GRATIS_ACIMA` | não | `8.00` / `120.00` |

## Banco

1. Crie o banco `cupcake` com `utf8mb4`.
2. Aplique `db/schema.sql` e, se quiser demonstração, `db/seed.sql`:

```bash
mariadb -h HOST -u USER -p BANCO < db/schema.sql
mariadb -h HOST -u USER -p BANCO < db/seed.sql
```

3. O banco `cupcake_test` **não** é necessário em produção.

## Build e execução local da imagem

```bash
docker build -t cupcake-gourmet .
docker run --rm --network host \
  -e APP_SECRET="troque-por-uma-chave-aleatoria" \
  -e DATABASE_URL="mariadb+pymysql://cupcake:cupcake@127.0.0.1:3307/cupcake?charset=utf8mb4" \
  cupcake-gourmet
```

A aplicação responde em `http://127.0.0.1:8000`. Verifique `GET /health`
(`{"status":"ok","db":"ok"}`).

## Plataformas

Qualquer plataforma que rode container e ofereça MySQL/MariaDB gerenciado serve:

- **Railway**: serviço a partir do repositório (Dockerfile) + plugin MySQL;
  copie `MYSQLURL` para `DATABASE_URL` e ajuste o esquema `mysql+pymysql://`.
- **Render**: Web Service (Docker) + banco MySQL externo (ex.: Aiven).
- **Fly.io**: `fly launch` com o Dockerfile + MySQL gerenciado.

Após o deploy:

1. Aplicar `schema.sql` e `seed.sql` no banco de produção.
2. Definir `APP_BASE_URL` e `SESSION_COOKIE_SECURE=true`.
3. Executar o roteiro do laudo com os cinco testadores.
4. Preencher a URL na tabela de entrega do `README.md`.

## Pendência

O provedor e as credenciais ainda não foram definidos; a imagem e as variáveis
acima são o contrato necessário para concluir a etapa.
