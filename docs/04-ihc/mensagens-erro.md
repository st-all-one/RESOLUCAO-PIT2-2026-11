# Catálogo de mensagens de erro

Toda mensagem exibida ao usuário tem código estável, texto, causa e ação esperada.
O código é renderizado em `data-codigo` para permitir teste automatizado e rastreio.

Formato de implementação: `core/problemas.py` mantém o `CATALOGO` (`código → status, título, detalhe`); os controllers levantam `ErroAplicacao(codigo)` e o handler central negocia HTML ou `application/problem+json`. Mensagens de sucesso/ajuste usam `avisar`/`avisar_codigo`, que gravam um flash na sessão e redirecionam com 303; o middleware drena o flash na requisição seguinte. Nenhuma stack trace chega ao usuário.

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
| `ERR-AUTH-009` | Autenticação necessária. | Rota protegida acessada sem sessão | Entrar na conta |
| `ERR-AUTH-010` | Muitas tentativas de acesso. Aguarde alguns minutos. | 5 falhas por conta e 30 por IP em 15 min | Aguardar e tentar novamente |

E-mail sem conta não é tratado como erro de credenciais: a tela de login mostra um
aviso informativo com link para o cadastro e preserva o e-mail digitado. `ERR-AUTH-001`
fica reservado para senha incorreta de uma conta existente.

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
| `ERR-CHK-004` | Não foi possível consultar o CEP agora. Preencha o endereço manualmente. | ViaCEP indisponível ou tempo esgotado | Preencher os campos manualmente |
| `ERR-CHK-005` | CEP não encontrado. Confira os 8 dígitos. | Código inexistente na base dos Correios | Corrigir o CEP |
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
| `ERR-ADM-010` | Envie uma imagem JPG, PNG ou WebP de até 2 MB. | Arquivo ausente, grande demais ou sem assinatura de imagem | Enviar outro arquivo |
| `ERR-ADM-008` | Já existe um produto com esse nome. | Unicidade de produto | Usar outro nome |
| `ERR-ADM-009` | Categoria não encontrada. | ID inexistente | Voltar à lista |
| `ERR-ENT-001` | Esta entrega não está atribuída a você. | Entregador diferente | Ver apenas as próprias entregas |
| `ERR-END-001` | Endereço não encontrado na sua conta. | Endereço inexistente ou de outro usuário | Voltar à conta e escolher um endereço próprio |

## Sistema

| Código | Texto ao usuário | Causa | Ação esperada |
|---|---|---|---|
| `ERR-SYS-001` | Não foi possível concluir a operação. Tente novamente. | Exceção não prevista | Repetir; se persistir, contatar a loja |
| `ERR-SYS-002` | Serviço temporariamente indisponível. | Banco inacessível | Aguardar e tentar novamente |
| `ERR-SYS-003` | Página não encontrada. | Rota inexistente | Voltar à vitrine |
| `ERR-SYS-004` | Este endereço não aceita o método usado. | Método HTTP incorreto | Usar o método indicado em `Allow` |
| `ERR-VAL-001` | Dados inválidos. Confira os campos destacados. | Payload malformado fora das validações específicas | Corrigir e reenviar |

## Transporte: Problem Details (RFC 9457)

Toda falha do back-end é representada pela mesma estrutura, independentemente do canal.
O formato segue a RFC 9457 (`application/problem+json`), com dois membros de extensão
obrigatórios: `codigo` e, em validação de formulário, `campos`.

```json
{
  "type": "https://cupcake-gourmet.local/problemas/err-auth-002",
  "title": "E-mail já cadastrado",
  "status": 409,
  "detail": "Este e-mail já está cadastrado.",
  "instance": "/cadastro",
  "codigo": "ERR-AUTH-002",
  "campos": {
    "email": "Este e-mail já está cadastrado."
  }
}
```

### Regras de negociação

| Cliente | Resposta |
|---|---|
| `Accept: application/problem+json` ou `application/json` | Corpo `application/problem+json` com o objeto acima |
| Navegador (`Accept: text/html`) | Página HTML com os mesmos campos renderizados, `data-codigo` e o JSON embutido em `data-problema`; o status HTTP é o mesmo |
| Rota de API e `/health` | Sempre `application/problem+json` em caso de falha |

### Campos

| Membro | Origem |
|---|---|
| `type` | URI estável derivada do código (`https://cupcake-gourmet.local/problemas/<codigo-em-minusculas>`) |
| `title` | Resumo curto do código, sem dados do usuário |
| `status` | Status HTTP da tabela abaixo |
| `detail` | Texto do catálogo, com parâmetros já interpolados |
| `instance` | Caminho da requisição (`request.url.path`) |
| `codigo` | Código estável deste catálogo (extensão) |
| `campos` | Mapa campo → mensagem, apenas em validação (extensão) |

### Status HTTP por código

| Código | Status | Código | Status |
|---|---|---|---|
| `ERR-AUTH-001` | 401 | `ERR-CAR-001` | 409 |
| `ERR-AUTH-002` | 409 | `ERR-CAR-002` | 409 |
| `ERR-AUTH-003..005` | 422 | `ERR-CAR-003` | 409 |
| `ERR-AUTH-006..008` | 403 | `ERR-CHK-001..003` | 422 |
| `ERR-AUTH-009` | 401 | `ERR-PAG-001` | 402 |
| `ERR-AUTH-010` | 429 | `ERR-PAG-002` | 422 |
| `ERR-CAT-001` | 404 | `ERR-PAG-003..004` | 409 |
| `ERR-CAT-002` | 409 | `ERR-ADM-001..002` | 409 |
| `ERR-CAT-003` | 422 | `ERR-ADM-003..004` | 422 |
| `ERR-PED-001` | 404 | `ERR-ADM-005` | 409 |
| `ERR-PED-002..003` | 409 | `ERR-ADM-006` | 404 |
| `ERR-PED-004` | 422 | `ERR-ADM-008` | 409 |
| `ERR-ENT-001` | 403 | `ERR-ADM-009` | 404 |
| `ERR-END-001` | 404 | `ERR-ADM-010` | 422 |
| `ERR-SYS-001` | 500 | `ERR-SYS-002` | 503 |
| `ERR-SYS-003` | 404 | `ERR-SYS-004` | 405 |
| `ERR-VAL-001` | 422 | | |

Códigos usados apenas como flash + 303 (`ERR-ADM-002`, `ERR-CAT-002`, `ERR-CAT-003`,
`ERR-CAR-003`, `ERR-PAG-001`) não geram corpo Problem Details; o
status da tabela vale quando a falha é levantada como `ErroAplicacao`.

### Implementação

1. `core/problemas.py` define `Problema` (dataclass imutável) com os membros RFC 9457,
   o mapa código → status e a serialização.
2. `ErroAplicacao(codigo, campos=...)` é a única exceção de domínio; o handler global a
   converte em `Problema` e negocia o formato pelo `Accept`.
3. Exceções inesperadas viram `ERR-SYS-001` (500), com log estruturado por `request_id`
   e sem PII; banco inacessível vira `ERR-SYS-002` (503).
4. Nenhuma `HTTPException` crua ou stack trace chega ao cliente.
5. Testes verificam status, `content-type`, `codigo`, `campos` e `instance` — tanto no
   caminho JSON quanto no HTML.
