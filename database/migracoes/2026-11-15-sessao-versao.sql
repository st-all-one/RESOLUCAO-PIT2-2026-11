-- Aplica em bancos existentes a versão de sessão usada pelo logout.
-- Execute uma vez: mariadb ... cupcake < database/migracoes/2026-11-15-sessao-versao.sql
-- A transação mantém a migração sob controle; no MariaDB, DDL pode fazer commit implícito.

START TRANSACTION;

ALTER TABLE usuarios
    ADD COLUMN IF NOT EXISTS sessao_versao INT NOT NULL DEFAULT 0 AFTER ativo;

COMMIT;
