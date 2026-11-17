-- Exclusão lógica de produtos: a linha permanece no banco e pode ser restaurada.
-- Execute uma vez: mariadb ... cupcake < database/migracoes/2026-11-17-exclusao-logica-produto.sql

START TRANSACTION;

ALTER TABLE produtos
    ADD COLUMN IF NOT EXISTS excluido_em TIMESTAMP NULL DEFAULT NULL AFTER ativo;

COMMIT;
