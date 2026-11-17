# Rastreabilidade — histórias, código, testes e documentos

Cada história de `docs/02-especificacao/cartoes.md` foi implementada e verificada.
Os testes citados ficam em `tests/` e rodam contra MariaDB real.

| História | Implementação principal | Verificação |
|---|---|---|
| US-01 Cadastro | `controllers/auth.py`, `services/seguranca.py`, `templates/auth/cadastro.html` | `test_auth.py::test_cadastro_autentica_e_grava_hash`, `::test_cadastro_com_email_repetido` |
| US-02 Login/logout | `controllers/auth.py`, `core/csrf.py`, `core/acesso.py` | `test_auth.py::test_login_e_logout`, `::test_login_com_senha_errada`, `::test_login_de_conta_desconhecida_sugere_cadastro`, `::test_login_de_conta_desativada` |
| US-03 Vitrine e busca | `controllers/catalogo.py`, `templates/catalogo/vitrine.html` | `test_catalogo.py::test_vitrine_lista_apenas_produtos_ativos`, `::test_busca_textual_filtra`, `::test_filtro_por_categoria` |
| US-04 Detalhe do produto | `controllers/catalogo.py`, `templates/catalogo/detalhe.html` | `test_catalogo.py::test_detalhe_por_slug`, `::test_detalhe_inexistente_em_json` |
| US-05 Carrinho | `services/carrinho.py`, `services/carrinho_db.py`, `controllers/carrinho.py` | `test_carrinho.py` (5 testes), `test_servicos.py::test_carrinho_puro_respeita_estoque` |
| US-06 Checkout e frete | `controllers/checkout.py`, `services/preco.py`, `services/validacao.py` | `test_compra.py::test_fluxo_pix_aprova_e_baixa_estoque`, `::test_consulta_cep_devolve_endereco`, `::test_checkout_permite_ajustar_item_sem_sair_da_tela`, `::test_pedido_exibe_codigo_publico_na_url`, `test_carrinho.py::test_frete_gratis_acima_do_limite` |
| US-07 Pagamento simulado | `services/pagamento.py`, `controllers/pagamento.py` | `test_compra.py::test_cartao_invalido_nao_baixa_estoque`, `::test_cartao_com_final_0000_e_recusado`, `test_servicos.py::test_luhn_e_simulacao_de_pagamento` |
| US-08 Acompanhamento | `controllers/pedidos.py`, `templates/pedidos/*` | `test_compra.py::test_fluxo_pix_aprova_e_baixa_estoque`, `::test_pedido_de_outro_cliente_nao_e_acessivel` |
| US-09 Cancelamento | `controllers/pedidos.py`, `services/operacoes.py` | `test_compra.py::test_cancelamento_estorna_pagamento_e_estoque` |
| US-10 Categorias | `controllers/admin.py`, `templates/admin/categorias.html` | `test_admin.py::test_admin_cria_categoria_e_produto_ativo` |
| US-11 Produtos e estoque | `controllers/admin.py`, `templates/admin/produto_form.html` | `test_admin.py::test_admin_cria_categoria_e_produto_ativo`, `::test_admin_rejeita_preco_invalido_e_nome_duplicado` |
| US-12 Gestão de pedidos | `controllers/admin.py`, `services/pedido.py` | `test_admin.py::test_transicoes_exigem_pagamento_e_entregador` |
| US-13 Relatório | `controllers/admin.py`, `templates/admin/relatorio.html` | `test_admin.py::test_relatorio_soma_pedidos_pagos` |
| US-14 Entregas | `controllers/entregas.py`, `templates/entregas/*` | `test_entregas.py` (3 testes) |
| US-15 Usuários | `controllers/admin.py`, `templates/admin/usuarios.html` | `test_admin.py::test_admin_nao_altera_a_propria_conta`, `test_auth.py::test_login_de_conta_desativada` |
| US-16 Conta e endereços | `controllers/conta.py`, `services/endereco.py`, `templates/conta/index.html` | `test_conta.py` (6 testes) |
| US-17 Carrinho no login | `controllers/auth.py::_iniciar_sessao` | `test_auth.py::test_login_preserva_carrinho_montado_como_visitante`, `::test_cadastro_preserva_carrinho_montado_como_visitante` |
| US-18 Imagem e lixeira | `controllers/admin.py`, `services/midia.py`, `templates/admin/produtos.html` | `test_admin.py::test_admin_cria_e_troca_imagem_do_produto`, `::test_admin_rejeita_arquivo_que_nao_e_imagem`, `::test_exclusao_logica_preserva_produto_e_restaura` |
| US-19 Endereço e mobile | `controllers/checkout.py`, `templates/checkout/form.html`, `frontend/src` | `test_compra.py::test_checkout_oferece_endereco_salvo_e_usa_o_escolhido`, `::test_checkout_nao_aceita_endereco_de_outra_conta` |

## Requisitos não funcionais

| RNF | Evidência |
|---|---|
| Segurança de senha (scrypt) | `services/seguranca.py`; hash verificado em `test_auth` |
| CSRF em toda mutação | `core/csrf.py`; `test_auth.py::test_mutacao_sem_csrf_e_rejeitada`, `::test_token_de_outra_sessao_e_rejeitado` |
| Estoque consistente | baixa condicional em `controllers/pagamento.py`; `test_compra.py::test_estoque_insuficiente_no_pagamento` |
| Problem Details RFC 9457 | `core/problemas.py`; `test_saude.py::test_rota_inexistente_em_json` |
| Mobile-first e acessibilidade AA | `static/css/estilo.css`; laudo `docs/07-laudo/laudo-qualidade.md` |
| Qualidade estática | `ruff`, `mypy strict`, ESLint, Stylelint — `make check` |
