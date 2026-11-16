# Deploy em VPS com Docker

A aplicação e o MariaDB rodam no mesmo `compose.yaml`. Na primeira subida, o
MariaDB executa `database/schema.sql` e `database/seed.sql` automaticamente; nas
seguintes, o volume `cupcake-mariadb-data` preserva os dados.

O modo `production` **recusa iniciar** com segredo de sessão fraco, sem HTTPS ou
com a senha de demonstração do administrador. Isso evita publicar um cookie
forjável ou o login `Admin@123` do seed.

## Pré-requisitos na VPS

- Docker Engine e plugin `docker compose`.
- Domínio apontando para a VPS (HTTPS obrigatório em produção).
- Proxy reverso com TLS (Caddy ou Nginx) na frente da aplicação.
- Repositório clonado.

## Primeira subida

```bash
cp .env.example .env
```

Edite o `.env`:

```env
APP_ENV=production
APP_SECRET=<saída de: openssl rand -hex 32>
APP_BASE_URL=https://cupcake.seu-dominio.com
SESSION_COOKIE_SECURE=true
MARIADB_ROOT_PASSWORD=<senha forte>
MARIADB_PASSWORD=<outra senha forte>
APP_BIND=127.0.0.1
APP_PORT=8000
```

O `DATABASE_URL` do `.env` precisa usar a mesma senha de `MARIADB_PASSWORD`.

1. Suba apenas o banco e troque a senha publicada do administrador:

```bash
make db-up
ADMIN_SENHA='<senha forte>' make admin-senha
```

2. Suba a aplicação (o build compila o TypeScript e instala o pacote Python):

```bash
make up
make ps
curl http://127.0.0.1:8000/health   # {"status":"ok","db":"ok"}
```

O `make up` espera o healthcheck do MariaDB e só então inicia a aplicação.

3. Publique via proxy HTTPS. Exemplo de `Caddyfile` no host:

```caddyfile
cupcake.seu-dominio.com {
    reverse_proxy 127.0.0.1:8000
}
```

A aplicação escuta apenas em `127.0.0.1`; não a exponha diretamente na internet.
Com `SESSION_COOKIE_SECURE=true` (ou `APP_BASE_URL=https://...`), o cookie de
sessão só trafega por HTTPS e a aplicação envia HSTS.

## Operação

```bash
make logs     # logs da aplicação
make ps       # estado dos containers
make down     # para aplicação e banco
make up       # aplica atualizações (rebuild da imagem)
```

Atualização:

```bash
git pull
make up
```

## Dados

- O schema roda uma única vez, quando o volume está vazio. Para recriar do zero
  **apagando os dados**: `docker compose down -v` e depois `make up`.
- Em um banco existente, aplique as migrações pendentes em
  `database/migracoes/` antes de subir a nova versão (por exemplo,
  `2026-11-15-sessao-versao.sql`).
- Backup lógico:

```bash
docker exec cupcake-mariadb mariadb-dump -uroot -p"$MARIADB_ROOT_PASSWORD" cupcake > backup.sql
```

- Restauração: `docker exec -i cupcake-mariadb mariadb -uroot -p"$MARIADB_ROOT_PASSWORD" cupcake < backup.sql`.

## Verificação pós-deploy

```bash
make deploy-check URL=https://cupcake.seu-dominio.com
```

Use `--email`/`--senha` no script (`backend/scripts/verificar_deploy.py`) porque a
senha do seed não é mais válida em produção. Roteiro manual complementar:

1. `GET /health` retorna `{"status":"ok","db":"ok"}` via HTTPS.
2. A vitrine lista os produtos do seed.
3. Login com o administrador e a senha definida em `make admin-senha`.
4. Fluxo completo: adicionar ao carrinho, checkout, PIX, acompanhar pedido.
5. Administração: criar produto, avançar status, conferir relatório.
6. Entregador: confirmar entrega.

O roteiro com os cinco testadores está em
`docs/07-laudo/template-laudo-testador.md`.

## Alternativa sem compose

A imagem também roda isolada:

```bash
docker build -t cupcake-gourmet .
docker run -d --restart unless-stopped \
  -p 127.0.0.1:8000:8000 \
  -e APP_ENV=production \
  -e APP_BASE_URL=https://cupcake.seu-dominio.com \
  -e SESSION_COOKIE_SECURE=true \
  -e APP_SECRET="..." \
  -e DATABASE_URL="mariadb+pymysql://usuario:senha@host:3306/banco?charset=utf8mb4" \
  cupcake-gourmet
```

Nesse caso o banco precisa ser criado e migrado manualmente com
`database/schema.sql` e, opcionalmente, `database/seed.sql`; troque a senha do
admin com `backend/scripts/definir_senha_admin.py` antes de liberar o acesso.
