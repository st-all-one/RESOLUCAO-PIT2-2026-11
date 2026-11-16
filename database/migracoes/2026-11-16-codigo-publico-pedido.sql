-- Código público do pedido: últimos 8 caracteres de um UUIDv7.
-- Pedidos antigos recebem um código aleatório; novos usam identificador.py.
-- A transação mantém a migração sob controle; no MariaDB, DDL pode fazer commit implícito.

START TRANSACTION;

ALTER TABLE pedidos
    ADD COLUMN IF NOT EXISTS codigo CHAR(8) NULL AFTER id;

UPDATE pedidos
SET codigo = LOWER(SUBSTRING(MD5(CONCAT(id, UUID(), RAND())), -8))
WHERE codigo IS NULL;

ALTER TABLE pedidos
    MODIFY codigo CHAR(8) NOT NULL;

CREATE UNIQUE INDEX IF NOT EXISTS uq_pedidos_codigo ON pedidos (codigo);

COMMIT;
