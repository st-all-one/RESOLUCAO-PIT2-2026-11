-- Cupcake Gourmet — projeto físico (MariaDB 11.4)
-- Uso: mariadb ... cupcake < database/schema.sql
-- O arquivo contém apenas DDL; o banco é selecionado pelo cliente.

SET NAMES utf8mb4;
SET FOREIGN_KEY_CHECKS = 0;

DROP TABLE IF EXISTS historico_pedido;
DROP TABLE IF EXISTS pagamentos;
DROP TABLE IF EXISTS itens_pedido;
DROP TABLE IF EXISTS pedidos;
DROP TABLE IF EXISTS enderecos;
DROP TABLE IF EXISTS produtos;
DROP TABLE IF EXISTS categorias;
DROP TABLE IF EXISTS usuarios;

SET FOREIGN_KEY_CHECKS = 1;

-- ---------------------------------------------------------------- usuarios
CREATE TABLE usuarios (
    id            BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    nome          VARCHAR(120)    NOT NULL,
    email         VARCHAR(254)    NOT NULL,
    senha_hash    VARCHAR(255)    NOT NULL,
    telefone      VARCHAR(11)     NULL,
    papel         VARCHAR(20)     NOT NULL DEFAULT 'cliente',
    ativo         BOOLEAN         NOT NULL DEFAULT TRUE,
    sessao_versao INT             NOT NULL DEFAULT 0,
    criado_em     TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP
                                  ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_usuarios_email (email),
    KEY ix_usuarios_papel (papel),
    CONSTRAINT ck_usuarios_papel
        CHECK (papel IN ('cliente', 'entregador', 'admin')),
    CONSTRAINT ck_usuarios_nome
        CHECK (CHAR_LENGTH(nome) BETWEEN 2 AND 120)
) ENGINE = InnoDB;

-- --------------------------------------------------------------- categorias
CREATE TABLE categorias (
    id        BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    nome      VARCHAR(80)     NOT NULL,
    slug      VARCHAR(80)     NOT NULL,
    ativo     BOOLEAN         NOT NULL DEFAULT TRUE,
    criado_em TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_categorias_nome (nome),
    UNIQUE KEY uq_categorias_slug (slug)
) ENGINE = InnoDB;

-- ----------------------------------------------------------------- produtos
CREATE TABLE produtos (
    id            BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    categoria_id  BIGINT UNSIGNED NOT NULL,
    nome          VARCHAR(120)    NOT NULL,
    slug          VARCHAR(140)    NOT NULL,
    imagem        VARCHAR(255)    NOT NULL DEFAULT '/static/img/produtos/padrao.jpg',
    descricao     TEXT            NOT NULL,
    alergenicos   VARCHAR(255)    NOT NULL,
    preco         DECIMAL(10, 2)  NOT NULL,
    estoque       INT             NOT NULL DEFAULT 0,
    ativo         BOOLEAN         NOT NULL DEFAULT TRUE,
    excluido_em   TIMESTAMP       NULL DEFAULT NULL,
    criado_em     TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP
                                  ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_produtos_slug (slug),
    KEY ix_produtos_categoria (categoria_id),
    KEY ix_produtos_ativo (ativo),
    CONSTRAINT ck_produtos_preco CHECK (preco > 0),
    CONSTRAINT ck_produtos_estoque CHECK (estoque >= 0),
    CONSTRAINT ck_produtos_nome CHECK (CHAR_LENGTH(nome) BETWEEN 2 AND 120),
    CONSTRAINT ck_produtos_descricao CHECK (CHAR_LENGTH(descricao) BETWEEN 1 AND 2000),
    CONSTRAINT fk_produtos_categoria FOREIGN KEY (categoria_id)
        REFERENCES categorias (id) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE = InnoDB;

-- ---------------------------------------------------------------- enderecos
CREATE TABLE enderecos (
    id          BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    usuario_id  BIGINT UNSIGNED NOT NULL,
    cep         CHAR(8)         NOT NULL,
    logradouro  VARCHAR(160)    NOT NULL,
    numero      VARCHAR(20)     NOT NULL,
    complemento VARCHAR(80)     NULL,
    bairro      VARCHAR(80)     NOT NULL,
    cidade      VARCHAR(80)     NOT NULL,
    uf          CHAR(2)         NOT NULL,
    principal   BOOLEAN         NOT NULL DEFAULT FALSE,
    criado_em   TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY ix_enderecos_usuario (usuario_id),
    CONSTRAINT ck_enderecos_cep CHECK (cep REGEXP '^[0-9]{8}$'),
    CONSTRAINT ck_enderecos_uf CHECK (uf REGEXP '^[A-Z]{2}$'),
    CONSTRAINT fk_enderecos_usuario FOREIGN KEY (usuario_id)
        REFERENCES usuarios (id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB;

-- ------------------------------------------------------------------ pedidos
-- Subtotal e total são derivados dos itens + frete (3FN); não são armazenados.
CREATE TABLE pedidos (
    id               BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    codigo           CHAR(8)         NOT NULL,
    cliente_id       BIGINT UNSIGNED NOT NULL,
    entregador_id    BIGINT UNSIGNED NULL,
    status           VARCHAR(20)     NOT NULL DEFAULT 'recebido',
    frete            DECIMAL(10, 2)  NOT NULL DEFAULT 0.00,
    cep              CHAR(8)         NOT NULL,
    logradouro       VARCHAR(160)    NOT NULL,
    numero           VARCHAR(20)     NOT NULL,
    complemento      VARCHAR(80)     NULL,
    bairro           VARCHAR(80)     NOT NULL,
    cidade           VARCHAR(80)     NOT NULL,
    uf               CHAR(2)         NOT NULL,
    telefone_contato VARCHAR(11)     NOT NULL,
    criado_em        TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em    TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP
                                     ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_pedidos_codigo (codigo),
    KEY ix_pedidos_cliente (cliente_id, criado_em),
    KEY ix_pedidos_status (status),
    KEY ix_pedidos_entregador (entregador_id),
    CONSTRAINT ck_pedidos_status
        CHECK (status IN ('recebido', 'em_preparo', 'saiu_entrega', 'entregue', 'cancelado')),
    CONSTRAINT ck_pedidos_frete CHECK (frete >= 0),
    CONSTRAINT ck_pedidos_uf CHECK (uf REGEXP '^[A-Z]{2}$'),
    CONSTRAINT fk_pedidos_cliente FOREIGN KEY (cliente_id)
        REFERENCES usuarios (id) ON DELETE RESTRICT ON UPDATE CASCADE,
    CONSTRAINT fk_pedidos_entregador FOREIGN KEY (entregador_id)
        REFERENCES usuarios (id) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE = InnoDB;

-- ------------------------------------------------------------- itens_pedido
-- nome_produto e preco_unitario são snapshots históricos: o preço do produto
-- pode mudar sem alterar o valor do pedido já fechado.
CREATE TABLE itens_pedido (
    id             BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    pedido_id      BIGINT UNSIGNED NOT NULL,
    produto_id     BIGINT UNSIGNED NOT NULL,
    nome_produto   VARCHAR(120)    NOT NULL,
    preco_unitario DECIMAL(10, 2)  NOT NULL,
    quantidade     INT             NOT NULL,
    PRIMARY KEY (id),
    UNIQUE KEY uq_itens_pedido_produto (pedido_id, produto_id),
    KEY ix_itens_produto (produto_id),
    CONSTRAINT ck_itens_preco CHECK (preco_unitario > 0),
    CONSTRAINT ck_itens_quantidade CHECK (quantidade > 0),
    CONSTRAINT fk_itens_pedido FOREIGN KEY (pedido_id)
        REFERENCES pedidos (id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_itens_produto FOREIGN KEY (produto_id)
        REFERENCES produtos (id) ON DELETE RESTRICT ON UPDATE CASCADE
) ENGINE = InnoDB;

-- --------------------------------------------------------------- pagamentos
-- valor é o montante autorizado no ato do pagamento (snapshot do total).
-- Nenhum dado completo de cartão é armazenado.
CREATE TABLE pagamentos (
    id                 BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    pedido_id          BIGINT UNSIGNED NOT NULL,
    metodo             VARCHAR(20)     NULL,
    status             VARCHAR(20)     NOT NULL DEFAULT 'pendente',
    valor              DECIMAL(10, 2)  NOT NULL,
    cartao_ultimos4    CHAR(4)         NULL,
    codigo_autorizacao VARCHAR(40)     NULL,
    criado_em          TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    atualizado_em      TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP
                                       ON UPDATE CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    UNIQUE KEY uq_pagamentos_pedido (pedido_id),
    CONSTRAINT ck_pagamentos_metodo
        CHECK (metodo IS NULL OR metodo IN ('pix', 'cartao')),
    CONSTRAINT ck_pagamentos_status
        CHECK (status IN ('pendente', 'aprovado', 'recusado', 'estornado', 'cancelado')),
    CONSTRAINT ck_pagamentos_valor CHECK (valor > 0),
    CONSTRAINT fk_pagamentos_pedido FOREIGN KEY (pedido_id)
        REFERENCES pedidos (id) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE = InnoDB;

-- --------------------------------------------------------- historico_pedido
CREATE TABLE historico_pedido (
    id         BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,
    pedido_id  BIGINT UNSIGNED NOT NULL,
    status     VARCHAR(20)     NOT NULL,
    usuario_id BIGINT UNSIGNED NULL,
    observacao VARCHAR(255)    NULL,
    criado_em  TIMESTAMP       NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (id),
    KEY ix_historico_pedido (pedido_id, criado_em),
    KEY ix_historico_usuario (usuario_id),
    CONSTRAINT ck_historico_status
        CHECK (status IN ('recebido', 'em_preparo', 'saiu_entrega', 'entregue', 'cancelado')),
    CONSTRAINT fk_historico_pedido FOREIGN KEY (pedido_id)
        REFERENCES pedidos (id) ON DELETE CASCADE ON UPDATE CASCADE,
    CONSTRAINT fk_historico_usuario FOREIGN KEY (usuario_id)
        REFERENCES usuarios (id) ON DELETE SET NULL ON UPDATE CASCADE
) ENGINE = InnoDB;
