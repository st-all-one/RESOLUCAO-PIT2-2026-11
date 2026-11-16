-- Cupcake Gourmet — dados de demonstração
-- Uso: mariadb ... cupcake < database/seed.sql
-- Senhas (hash scrypt): Admin@123, Cliente@123, Entrega@123, Maria@123.

SET NAMES utf8mb4;

DELETE FROM historico_pedido;
DELETE FROM pagamentos;
DELETE FROM itens_pedido;
DELETE FROM pedidos;
DELETE FROM enderecos;
DELETE FROM produtos;
DELETE FROM categorias;
DELETE FROM usuarios;

-- ---------------------------------------------------------------- usuarios
INSERT INTO usuarios (id, nome, email, senha_hash, telefone, papel, ativo) VALUES
(1, 'Administrador', 'admin@cupcake.local',
 'scrypt$16384$8$1$W7405REaV+oVrFYbIhCs+w==$rgaqWH47ECWsb1PiM5ZK46UG+C2lENC6N3OHSFiwUyoW2ftJ+oSRRT8pyRLfEU7QWORdHaHxSIzTgWBttLZxTQ==',
 '11999990000', 'admin', TRUE),
(2, 'Cliente Demonstração', 'cliente@cupcake.local',
 'scrypt$16384$8$1$ooEA6EIPOZYTReHBRRHkIw==$M2kpv2AHHjNCKXTOe3qUZSUzZoL8FZDFPk4LRJ6jcNfl02eV0JDpneLMNNe0PRcnTKtpHRcHLz3N8Oq83oasFA==',
 '11999990001', 'cliente', TRUE),
(3, 'Entregador Demonstração', 'entregador@cupcake.local',
 'scrypt$16384$8$1$dkogBaFKiZexL/O+GAC/Eg==$umjgVj7IKypjlUReBe1f9MUj8ap+O4TQORKBlh0SZlLfWEP4/qyHvtXJmq5E9FJY2a61dLdchKDjCaqgW6i+og==',
 '11999990002', 'entregador', TRUE),
(4, 'Maria Souza', 'maria@cupcake.local',
 'scrypt$16384$8$1$YXwqBU6H15Igc4JY3XJs0Q==$6LuioJhfSHld0ghuCLE23WTdU336M56EcY+/j2uEw9aP3sn264l+LL5PZQjNcgxLv/U6jcMiPqY8x4Ekcdr/rg==',
 '11999990003', 'cliente', TRUE);

-- --------------------------------------------------------------- categorias
INSERT INTO categorias (id, nome, slug, ativo) VALUES
(1, 'Clássicos', 'classicos', TRUE),
(2, 'Recheados', 'recheados', TRUE),
(3, 'Veganos', 'veganos', TRUE),
(4, 'Sazonais', 'sazonais', TRUE);

-- ----------------------------------------------------------------- produtos
INSERT INTO produtos
    (id, categoria_id, nome, slug, imagem, descricao, alergenicos, preco, estoque, ativo) VALUES
(1, 1, 'Baunilha Clássico', 'baunilha-classico',
 '/static/img/produtos/baunilha-classico.jpg',
 'Massa de baunilha com buttercream de baunilha e raspas de fava.',
 'Contém gluten, leite e ovos.', 9.90, 20, TRUE),
(2, 1, 'Chocolate Belga', 'chocolate-belga',
 '/static/img/produtos/chocolate-belga.jpg',
 'Massa de cacau 70% com ganache de chocolate belga.',
 'Contém gluten, leite, ovos e soja.', 11.50, 15, TRUE),
(3, 2, 'Red Velvet', 'red-velvet',
 '/static/img/produtos/red-velvet.jpg',
 'Massa vermelha de cacau com cream cheese frosting.',
 'Contém gluten, leite e ovos.', 12.90, 12, TRUE),
(4, 2, 'Ninho com Nutella', 'ninho-nutella',
 '/static/img/produtos/ninho-nutella.jpg',
 'Massa de leite Ninho recheada com Nutella.',
 'Contém gluten, leite, ovos e avelã.', 14.50, 10, TRUE),
(5, 2, 'Morango Cream', 'morango-cream',
 '/static/img/produtos/morango-cream.jpg',
 'Massa branca com creme de morango fresco.',
 'Contém gluten, leite e ovos.', 12.50, 8, TRUE),
(6, 1, 'Limão Siciliano', 'limao-siciliano',
 '/static/img/produtos/limao-siciliano.jpg',
 'Massa cítrica com curd de limão siciliano.',
 'Contém gluten, leite e ovos.', 11.90, 0, TRUE),
(7, 3, 'Vegano Coco', 'vegano-coco',
 '/static/img/produtos/vegano-coco.jpg',
 'Massa vegana de coco com creme de coco.',
 'Contém coco. Sem ingredientes de origem animal.', 10.90, 9, TRUE),
(8, 3, 'Vegano Chocolate', 'vegano-chocolate',
 '/static/img/produtos/vegano-chocolate.jpg',
 'Massa vegana de cacau com ganache de chocolate amargo.',
 'Contém cacau e soja. Sem ingredientes de origem animal.', 11.90, 7, TRUE),
(9, 2, 'Cenoura com Brigadeiro', 'cenoura-brigadeiro',
 '/static/img/produtos/cenoura-brigadeiro.jpg',
 'Massa de cenoura com brigadeiro cremoso.',
 'Contém gluten, leite e ovos.', 12.90, 14, TRUE),
(10, 4, 'Pistache', 'pistache',
 '/static/img/produtos/pistache.jpg',
 'Massa de pistache com creme de pistache e flor de sal.',
 'Contém gluten, leite, ovos e pistache.', 16.90, 6, TRUE),
(11, 4, 'Abóbora com Especiarias', 'abobora-especiarias',
 '/static/img/produtos/abobora-especiarias.jpg',
 'Massa de abóbora com canela, gengibre e noz-moscada.',
 'Contém gluten, leite e ovos.', 13.90, 5, TRUE),
(12, 4, 'Frutas Vermelhas', 'frutas-vermelhas',
 '/static/img/produtos/frutas-vermelhas.jpg',
 'Massa branca com compota de frutas vermelhas.',
 'Contém gluten, leite e ovos.', 13.50, 0, TRUE);

-- ---------------------------------------------------------------- enderecos
INSERT INTO enderecos
    (id, usuario_id, cep, logradouro, numero, complemento, bairro, cidade, uf, principal) VALUES
(1, 2, '01310100', 'Avenida Paulista', '1000', 'Apto 42', 'Bela Vista', 'São Paulo', 'SP', TRUE),
(2, 4, '04538132', 'Rua dos Pinheiros', '250', NULL, 'Pinheiros', 'São Paulo', 'SP', TRUE);

-- ------------------------------------------------------------------ pedidos
INSERT INTO pedidos
    (id, cliente_id, entregador_id, status, frete, cep, logradouro, numero,
     complemento, bairro, cidade, uf, telefone_contato, criado_em) VALUES
(1, 2, 3, 'entregue', 8.00, '01310100', 'Avenida Paulista', '1000',
 'Apto 42', 'Bela Vista', 'São Paulo', 'SP', '11999990001',
 NOW() - INTERVAL 3 DAY),
(2, 2, NULL, 'recebido', 8.00, '01310100', 'Avenida Paulista', '1000',
 'Apto 42', 'Bela Vista', 'São Paulo', 'SP', '11999990001',
 NOW() - INTERVAL 2 HOUR),
(3, 2, 3, 'em_preparo', 0.00, '01310100', 'Avenida Paulista', '1000',
 'Apto 42', 'Bela Vista', 'São Paulo', 'SP', '11999990001',
 NOW() - INTERVAL 1 DAY);

-- ------------------------------------------------------------- itens_pedido
INSERT INTO itens_pedido (pedido_id, produto_id, nome_produto, preco_unitario, quantidade) VALUES
(1, 1, 'Baunilha Clássico', 9.90, 1),
(1, 2, 'Chocolate Belga', 11.50, 2),
(2, 3, 'Red Velvet', 12.90, 1),
(3, 4, 'Ninho com Nutella', 14.50, 3),
(3, 10, 'Pistache', 16.90, 3),
(3, 9, 'Cenoura com Brigadeiro', 12.90, 2);

-- --------------------------------------------------------------- pagamentos
INSERT INTO pagamentos
    (pedido_id, metodo, status, valor, cartao_ultimos4, codigo_autorizacao, criado_em) VALUES
(1, 'pix', 'aprovado', 40.90, NULL, 'PIX-SEED-0001', NOW() - INTERVAL 3 DAY),
(2, NULL, 'pendente', 20.90, NULL, NULL, NOW() - INTERVAL 2 HOUR),
(3, 'pix', 'aprovado', 120.00, NULL, 'PIX-SEED-0003', NOW() - INTERVAL 1 DAY);

-- --------------------------------------------------------- historico_pedido
INSERT INTO historico_pedido (pedido_id, status, usuario_id, observacao, criado_em) VALUES
(1, 'recebido', 2, 'Pedido criado no checkout.', NOW() - INTERVAL 3 DAY),
(1, 'em_preparo', 1, 'Pagamento aprovado; produção iniciada.', NOW() - INTERVAL 3 DAY + INTERVAL 20 MINUTE),
(1, 'saiu_entrega', 1, 'Entregador atribuído.', NOW() - INTERVAL 3 DAY + INTERVAL 50 MINUTE),
(1, 'entregue', 3, 'Entrega confirmada pelo entregador.', NOW() - INTERVAL 3 DAY + INTERVAL 90 MINUTE),
(2, 'recebido', 2, 'Pedido criado no checkout.', NOW() - INTERVAL 2 HOUR),
(3, 'recebido', 2, 'Pedido criado no checkout.', NOW() - INTERVAL 1 DAY),
(3, 'em_preparo', 1, 'Pagamento aprovado; produção iniciada.', NOW() - INTERVAL 1 DAY + INTERVAL 30 MINUTE);
