# Operação (runbook)

## Deploy na VPS

```bash
git pull
cp .env.example .env    # na primeira vez; defina APP_SECRET e senhas
make up                 # build + banco + aplicação
make ps
make deploy-check URL=http://SEU_IP_OU_DOMINIO:8000
```

O primeiro `make up` aplica `database/schema.sql` e `database/seed.sql` no volume
novo. Subidas seguintes preservam os dados. As imagens enviadas pelo admin vivem
no volume `cupcake-uploads`, montado em `/app/uploads`.

## Atualização

```bash
git pull
make up        # rebuild da imagem; reinicia a aplicação
make logs      # acompanhe erros de inicialização
```

Se o schema mudou, aplique a alteração antes de subir a nova versão. Não há
migração automática; veja [desenvolvimento.md](desenvolvimento.md).

## Backup e restauração

```bash
# backup
docker exec cupcake-mariadb mariadb-dump -uroot -p"$MARIADB_ROOT_PASSWORD" cupcake > backup.sql

# restauração
docker exec -i cupcake-mariadb mariadb -uroot -p"$MARIADB_ROOT_PASSWORD" cupcake < backup.sql

# imagens enviadas (volume)
docker run --rm -v cupcake-uploads:/dados -v "$PWD":/backup alpine \
  tar czf /backup/uploads.tar.gz -C /dados .
```

Teste a restauração em um banco separado antes de confiar no backup.

## Saúde e logs

```bash
curl http://127.0.0.1:8000/health     # {"status":"ok","db":"ok"}
docker compose ps                     # estados e healthchecks
docker compose logs -f app            # aplicação
docker compose logs -f mariadb        # banco
```

## Sintomas e ações

| Sintoma | Causa provável | Ação |
|---|---|---|
| `health` 503 / app unhealthy | banco fora ou senha divergente | `docker compose ps`, logs do MariaDB, conferir `MARIADB_PASSWORD` e `DATABASE_URL` |
| Login não persiste em HTTPS | cookie `Secure` com HTTP | `SESSION_COOKIE_SECURE=false` ou termine TLS no proxy |
| 500 em página | exceção não tratada | logs `app`; o `request_id` aparece no rodapé |
| 502 no proxy | app não subiu | `docker compose logs app` |
| Volume cheio | logs/dados | `docker system df`, limpar imagens antigas |
| Seed ausente | volume já existia vazio | aplicar `database/schema.sql` e `seed.sql` manualmente |
| Imagem enviada some após deploy | volume `cupcake-uploads` não montado | conferir `docker inspect cupcake-app` e o `compose.yaml` |
| Produto excluído não aparece | está na lixeira | `/admin/produtos?lixeira=1` → Restaurar |

## Rollback

1. `git checkout <commit-anterior>` (ou `git revert`).
2. `make up` para reconstruir.
3. Se a alteração envolveu schema, restaure o backup correspondente.

## Segurança operacional

- Nunca versione `.env`; ele contém `APP_SECRET` e senhas.
- Troque as senhas padrão do seed em produção.
- Exponha apenas a porta da aplicação; o MariaDB fica em `127.0.0.1:3307`.
- Use HTTPS e `SESSION_COOKIE_SECURE=true` em domínio público.
- Faça backup antes de qualquer alteração de schema.
