# Deploy em VPS com Docker

A aplicação e o MariaDB rodam no mesmo `compose.yaml`. Na primeira subida, o
MariaDB executa `database/schema.sql` e `database/seed.sql` automaticamente; nas seguintes,
o volume `cupcake-mariadb-data` preserva os dados.

## Pré-requisitos na VPS

- Docker Engine e plugin `docker compose`.
- Porta escolhida liberada no firewall (padrão `8000`).
- Repositório clonado.

## Primeira subida

```bash
cp .env.example .env
# edite o .env:
#   APP_SECRET=<chave aleatória de 32+ bytes>
#   MARIADB_PASSWORD=<senha forte>
#   MARIADB_ROOT_PASSWORD=<senha forte>
#   APP_BASE_URL=http://SEU_IP_OU_DOMINIO:8000
#   SESSION_COOKIE_SECURE=false   (true apenas com HTTPS)
make up
make ps
curl http://127.0.0.1:8000/health   # {"status":"ok","db":"ok"}
```

`make up` executa `docker compose up -d --build`: compila o TypeScript, instala
o pacote Python, sobe o MariaDB, espera o healthcheck e só então inicia a
aplicação (`depends_on: condition: service_healthy`).

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
- Backup lógico:

```bash
docker exec cupcake-mariadb mariadb-dump -uroot -p"$MARIADB_ROOT_PASSWORD" cupcake > backup.sql
```

- Restauração: `docker exec -i cupcake-mariadb mariadb -uroot -p"$MARIADB_ROOT_PASSWORD" cupcake < backup.sql`.

## HTTPS

Para usar domínio e HTTPS, coloque um proxy reverso na frente (Caddy ou Nginx)
apontando para `127.0.0.1:8000` e ajuste:

```env
APP_BASE_URL=https://cupcake.seu-dominio.com
SESSION_COOKIE_SECURE=true
```

Sem HTTPS, mantenha `SESSION_COOKIE_SECURE=false`, caso contrário o navegador
não envia o cookie de sessão e o login não persiste.

## Verificação pós-deploy

Um comando valida health, vitrine, detalhe, login e administração:

```bash
make deploy-check URL=http://SEU_IP_OU_DOMINIO:8000
```

Use `--email`/`--senha` no script (`backend/scripts/verificar_deploy.py`) se a conta
administrativa não for a do seed. Roteiro manual complementar:

1. `GET /health` retorna `{"status":"ok","db":"ok"}`.
2. Vitrine lista os 12 produtos do seed.
3. Login com `admin@cupcake.local` / `Admin@123`.
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
  -p 8000:8000 \
  -e APP_SECRET="..." \
  -e DATABASE_URL="mariadb+pymysql://usuario:senha@host:3306/banco?charset=utf8mb4" \
  cupcake-gourmet
```

Nesse caso o banco precisa ser criado e migrado manualmente com
`database/schema.sql` e, opcionalmente, `database/seed.sql`.
