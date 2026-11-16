# Catálogo de mensagens de erro

Toda mensagem exibida ao usuário tem código estável, texto, causa e ação esperada.
O código é renderizado em `data-codigo` para permitir teste automatizado e rastreio.

Formato de implementação: `core/mensagens.py` mantém o mapa `código → texto`; os
controllers levantam `ErroAplicacao(codigo)` e o handler central converte em flash
message + HTTP status. Nenhuma stack trace chega ao usuário.

## Autenticação e autorização

| Código | Texto ao usuário | Causa | Ação esperada |
|---|---|---|---|
| `ERR-AUTH-001` | E-mail ou senha inválidos. | Credenciais não conferem | Corrigir e tentar novamente |
| `ERR-AUTH-002` | Este e-mail já está cadastrado. | Violação de unicidade | Fazer login ou usar outro e-mail |
| `ERR-AUTH-003` | A senha precisa ter ao menos 8 caracteres, com letra e número. | Senha fora da política | Informar senha válida |
| `ERR-AUTH-004` | As senhas não conferem. | Confirmação divergente | Repetir a senha |
| `ERR-AUTH-005` | Informe nome e e-mail válidos. | Campo vazio ou e-mail malformado | Corrigir os campos |
| `ERR-AUTH-006` | Esta conta está desativada. Procure o administrador. | `ativo = false` | Contatar a loja |
| `ERR-AUTH-007` | Você não tem permissão para acessar esta área. | Papel insuficiente | Voltar à área permitida |
| `ERR-AUTH-008` | Sua sessão expirou. Entre novamente. | Sessão ausente, expirada ou CSRF inválido | Refazer o login |

## Catálogo e carrinho

| Código | Texto ao usuário | Causa | Ação esperada |
|---|---|---|---|
| `ERR-CAT-001` | Produto não encontrado. | Slug inexistente ou inativo | Voltar à vitrine |
| `ERR-CAT-002` | Este produto está esgotado. | Estoque zero | Escolher outro produto |
| `ERR-CAT-003` | Informe uma quantidade válida. | Quantidade ≤ 0 ou não numérica | Ajustar a quantidade |
| `ERR-CAR-001` | Seu carrinho está vazio. | Checkout sem itens | Adicionar produtos |
| `ERR-CAR-002` | Quantidade acima do estoque disponível. | Pedido maior que `estoque` | Reduzir a quantidade |
| `ERR-CAR-003` | O carrinho foi atualizado porque um item esgotou. | Estoque mudou entre adição e checkout | Revisar o carrinho |

## Checkout e pagamento

| Código | Texto ao usuário | Causa | Ação esperada |
|---|---|---|---|
| `ERR-CHK-001` | Preencha todos os campos obrigatórios do endereço. | Campo vazio | Completar o endereço |
| `ERR-CHK-002` | CEP inválido. Informe 8 dígitos. | CEP fora do padrão | Corrigir o CEP |
| `ERR-CHK-003` | UF inválida. | UF diferente de 2 letras | Corrigir a UF |
| `ERR-PAG-001` | Pagamento recusado pela operadora simulada. | Regra de recusa (final 0000) | Tentar outro método |
| `ERR-PAG-002` | Número de cartão inválido. | Falha na validação de Luhn | Conferir o número |
| `ERR-PAG-003` | Este pedido já está pago. | Pagamento aprovado repetido | Ir para o acompanhamento |
| `ERR-PAG-004` | Estoque insuficiente para concluir o pagamento. | Concorrência no estoque | Revisar o carrinho |

## Pedidos

| Código | Texto ao usuário | Causa | Ação esperada |
|---|---|---|---|
| `ERR-PED-001` | Pedido não encontrado. | ID inexistente ou de outro usuário | Voltar à lista |
| `ERR-PED-002` | Transição de status inválida. | Mudança fora da máquina de estados | Escolher transição permitida |
| `ERR-PED-003` | Este pedido não pode mais ser cancelado. | Status posterior a `recebido` (cliente) | Contatar a loja |
| `ERR-PED-004` | O pedido não possui itens. | Carrinho inconsistente | Refazer o pedido |

## Administração e entrega

| Código | Texto ao usuário | Causa | Ação esperada |
|---|---|---|---|
| `ERR-ADM-001` | Informe um nome de categoria único. | Vazio ou duplicado | Usar outro nome |
| `ERR-ADM-002` | A categoria possui produtos e não pode ser excluída. | FK `RESTRICT` | Desativar a categoria |
| `ERR-ADM-003` | O preço deve ser maior que zero. | Preço ≤ 0 | Informar preço válido |
| `ERR-ADM-004` | O estoque não pode ser negativo. | Estoque < 0 | Corrigir o estoque |
| `ERR-ADM-005` | Você não pode desativar a própria conta. | Auto-bloqueio | Pedir a outro administrador |
| `ERR-ADM-006` | Usuário não encontrado. | ID inexistente | Voltar à lista |
| `ERR-ADM-007` | O produto possui histórico de pedidos e não pode ser excluído. | FK `RESTRICT` | Desativar o produto |
| `ERR-ENT-001` | Esta entrega não está atribuída a você. | Entregador diferente | Ver apenas as próprias entregas |

## Sistema

| Código | Texto ao usuário | Causa | Ação esperada |
|---|---|---|---|
| `ERR-SYS-001` | Não foi possível concluir a operação. Tente novamente. | Exceção não prevista | Repetir; se persistir, contatar a loja |
| `ERR-SYS-002` | Serviço temporariamente indisponível. | Banco inacessível | Aguardar e tentar novamente |

## Regra de implementação

1. Toda validação de servidor retorna um código deste catálogo.
2. O handler global captura `ErroAplicacao`, grava flash e responde com o status da
   tabela (400, 403, 404, 409, 422).
3. Exceções inesperadas viram `ERR-SYS-001`, com log estruturado sem PII.
4. Testes verificam o código em `data-codigo`, não o texto livre.
