-- Imagem ilustrativa de cada produto.
-- Execute uma vez: mariadb ... cupcake < database/migracoes/2026-11-16-imagem-produto.sql
-- A transação mantém a migração sob controle; no MariaDB, DDL pode fazer commit implícito.

START TRANSACTION;

ALTER TABLE produtos
    ADD COLUMN IF NOT EXISTS imagem VARCHAR(255) NOT NULL
        DEFAULT '/static/img/produtos/padrao.jpg' AFTER slug;

UPDATE produtos
SET imagem = CASE slug
    WHEN 'baunilha-classico' THEN '/static/img/produtos/baunilha-classico.jpg'
    WHEN 'chocolate-belga' THEN '/static/img/produtos/chocolate-belga.jpg'
    WHEN 'red-velvet' THEN '/static/img/produtos/red-velvet.jpg'
    WHEN 'ninho-nutella' THEN '/static/img/produtos/ninho-nutella.jpg'
    WHEN 'morango-cream' THEN '/static/img/produtos/morango-cream.jpg'
    WHEN 'limao-siciliano' THEN '/static/img/produtos/limao-siciliano.jpg'
    WHEN 'vegano-coco' THEN '/static/img/produtos/vegano-coco.jpg'
    WHEN 'vegano-chocolate' THEN '/static/img/produtos/vegano-chocolate.jpg'
    WHEN 'cenoura-brigadeiro' THEN '/static/img/produtos/cenoura-brigadeiro.jpg'
    WHEN 'pistache' THEN '/static/img/produtos/pistache.jpg'
    WHEN 'abobora-especiarias' THEN '/static/img/produtos/abobora-especiarias.jpg'
    WHEN 'frutas-vermelhas' THEN '/static/img/produtos/frutas-vermelhas.jpg'
    ELSE imagem
END;

COMMIT;
