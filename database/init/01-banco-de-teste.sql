-- Cria o banco usado pela suíte automatizada (ver tests/conftest.py).
-- Executado apenas na primeira inicialização do volume do MariaDB.
CREATE DATABASE IF NOT EXISTS cupcake_test
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

GRANT ALL PRIVILEGES ON cupcake_test.* TO 'cupcake'@'%';
FLUSH PRIVILEGES;
