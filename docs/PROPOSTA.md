# Proposta de Modelagem Profunda do Domínio

## Contexto do domínio

O sistema modela uma Distribuidora de Bebidas em Alta Escala. A preocupação principal não é criar um CRUD, mas representar as regras de negócio que envolvem produtos, lotes, estoque, pedidos, separação, movimentações e expedição.

A modelagem foi orientada por DDD tático, encapsulamento e colaboração entre objetos. As regras importantes foram posicionadas nos objetos que possuem responsabilidade direta sobre elas, evitando que `main.py`, JSON ou testes se tornem donos das decisões do negócio.

---

## 1. Objetos que possuem identidade

Objetos com identidade têm ciclo de vida próprio e continuam sendo o mesmo objeto mesmo quando seus atributos mudam.

| Conceito do negócio | Classe | Por que possui identidade |
|---|---|---|
| Pedido | `Order` | Tem `PedidoId`, ciclo de estados, itens, expedição, rastreio e histórico persistido em JSON. |
| Produto | `Product` | Tem identificador próprio, código de barras, marca, categoria, preço e saldo físico agregado. |
| Lote | `Batch` | Tem `BatchId`, validade e quantidade atual. Dois lotes do mesmo produto não são o mesmo lote. |
| Fornecedor | `Fornecedor` | Tem `FornecedorId`, CNPJ, telefone e e-mail. Identifica quem fornece produtos. |
| Movimentação de estoque | `StockMovement` | Tem `MovimentacaoId`, tipo, data, produto, lote e motivo. Serve como registro de rastreabilidade. |
| Cliente | `ClienteId` | Ainda não existe como entidade completa, mas o pedido já preserva a identidade do cliente por `ClienteId`. |
| Usuário/Role | `User` e `Role` | Ainda estão como cadastro mockado em `main.py`. Eles representam identidade administrativa, mas não são o núcleo do domínio de separação/expedição. |

Decisão: `Order` é o agregado mais importante do fluxo comercial; `StockRegistry` concentra o agregado operacional de estoque.

---

## 2. Conceitos que são valores

Value Objects não têm identidade própria. Eles existem para proteger formatos, validações e regras pequenas, evitando primitivos soltos pelo sistema.

| Conceito | Classe | Regra protegida |
|---|---|---|
| CPF | `CPF` | Formato e dígitos verificadores. |
| CNPJ | `CNPJ` | Formato e dígitos verificadores. |
| E-mail | `Email` | Normalização e formato válido. |
| Telefone | `PhoneNumber` | DDD, celular e fixo válidos. |
| Endereço | `Address` | CEP, rua, número, bairro, cidade e UF válidos. |
| Dinheiro | `Money` | Valor monetário em centavos e formato brasileiro. |
| Quantidade | `Quantity` | Quantidade não negativa e operações de soma/subtração seguras. |
| Faixa de validade | `ValidityWindow` | Regra de lote vencido por data de referência. |
| Identificadores | `EntityId`, `PedidoId`, `BatchId`, etc. | Identidade imutável baseada em UUID. |
| Item de pedido | `OrderItem` | Não tem ID próprio; pertence ao agregado `Order` e sabe calcular total e marcar separação. |

Decisão: `OrderItem` foi mantido como componente do agregado `Order`, pois não precisa ser consultado nem persistido isoladamente.

---

## 3. Objetos que devem ter comportamento

A modelagem evita objetos que só guardam dados. Cada objeto relevante recebe operações com linguagem do negócio.

### `Product`

Responsabilidades:

- validar identificação, marca, nome, preço e estoque inicial;
- classificar bebida por `BeverageCategory`;
- adicionar e remover estoque físico agregado;
- alterar preço e descrição com validação;
- exportar snapshot para JSON.

Métodos principais:

- `classify_as(...)`
- `is_from_category(...)`
- `add_stock(...)`
- `remove_stock(...)`
- `change_price(...)`
- `to_dict()`

### `Batch`

Responsabilidades:

- proteger validade do lote;
- proteger quantidade inicial e atual;
- consumir quantidade sem permitir saldo negativo;
- informar se pode suprir uma demanda.

Métodos principais:

- `is_expired(...)`
- `can_supply(...)`
- `consume_amount(...)`
- `to_dict()`

### `StockRegistry`

Responsabilidades:

- receber lotes;
- calcular saldo por produto com base em lotes válidos;
- realizar baixa de estoque;
- registrar movimentações de entrada e saída;
- aplicar política de seleção de lotes.

Métodos principais:

- `receive_batch(...)`
- `balance_for_product(...)`
- `withdraw_fefo(...)`
- `withdraw(...)`
- `list_history()`
- `to_dict()`

### `Order`

Responsabilidades:

- proteger ciclo de vida do pedido;
- permitir alteração de itens somente antes da confirmação;
- calcular total financeiro;
- calcular total físico separado;
- validar separação total;
- expedir somente quando o pedido estiver separado;
- gerar rastreio simples.

Métodos principais:

- `confirm_payment()`
- `mark_as_separated()`
- `ship()`
- `cancel_order()`
- `end_order()`
- `get_separate_financial_total()`
- `get_separate_physical_amount()`
- `to_dict()`

### `OrderItem`

Responsabilidades:

- validar produto, quantidade e preço unitário;
- calcular total do item;
- registrar quantidade separada;
- indicar se está totalmente separado.

Métodos principais:

- `get_total()`
- `mark_separated(...)`
- `is_fully_separated()`

### `TotalSeparation`

Responsabilidades:

- coordenar a separação total de um pedido;
- validar disponibilidade antes de consumir estoque;
- garantir que não exista separação parcial inconsistente;
- delegar baixa de estoque para `StockRegistry`;
- marcar pedido como separado somente depois da separação completa.

Método principal:

- `execute(...)`

### `OrderWorkflow`

Responsabilidades:

- coordenar o caso de uso de confirmação, separação e expedição;
- receber dependências por injeção manual;
- salvar o pedido pelo repositório;
- acionar notificação após expedição.

Decisão: `OrderWorkflow` não concentra regra de negócio. Ele apenas orquestra objetos do domínio.

---

## 4. Onde ficam as regras de pedido, estoque, separação e expedição

### Regras de pedido

Ficam em `Order`.

Regras protegidas:

- pedido inicia em `AGUARDANDO PAGAMENTO`;
- só pode ir para `EM PROCESSAMENTO` após `confirm_payment()`;
- itens só podem ser alterados antes da confirmação;
- pedido só pode ser marcado como `SEPARADO` se todos os itens estiverem totalmente separados;
- pedido não pode pular transições inválidas;
- estados terminais não aceitam novas transições livres.

### Regras de estoque

Ficam em `StockRegistry`, `Batch` e `StockMovement`.

Regras protegidas:

- estoque não é apenas um número solto;
- saldo é calculado por lotes válidos;
- lote vencido não entra em saldo disponível;
- baixa não pode deixar lote negativo;
- toda entrada e saída gera `StockMovement`;
- seleção de lotes é definida por política injetada.

### Regras de separação

Ficam em `TotalSeparation`, com colaboração de `StockRegistry`, `Batch`, `Order` e `OrderItem`.

Regras protegidas:

- pedido precisa estar em `EM PROCESSAMENTO`;
- disponibilidade é validada antes da baixa;
- lote vencido é ignorado;
- baixa usa política de lotes, por padrão FEFO;
- item registra sua quantidade separada;
- pedido só muda para `SEPARADO` depois de todos os itens completos.

### Regras de expedição

Ficam em `Order.ship()`.

Regras protegidas:

- expedição só ocorre se o pedido estiver `SEPARADO`;
- pedido não pode ser expedido duas vezes;
- data de expedição é registrada no próprio pedido;
- código de rastreio é gerado no próprio pedido;
- status muda para `EM TRANSPORTE` por transição válida.

### Regras de persistência simulada

Ficam em `JsonOrderRepository` e `json_storage.py`.

Decisão: JSON não contém regra de negócio. Ele apenas armazena snapshots.

---

## 5. Como evitar modelo anêmico

A solução evita modelo anêmico pelas seguintes decisões:

1. Status do pedido não deve ser manipulado livremente por código externo. O fluxo usa métodos de negócio como `confirm_payment()`, `mark_as_separated()` e `ship()`.
2. Estoque não é representado apenas por um inteiro. Ele é composto por lotes, movimentos e saldo calculado.
3. Lote possui comportamento de validade e consumo, não apenas dados.
4. Item de pedido sabe calcular total e registrar separação.
5. Separação é uma colaboração entre pedido, estoque, lotes e itens, não um procedimento solto em `main.py`.
6. Persistência JSON fica atrás de repositórios, impedindo que arquivos decidam regra de domínio.
7. Políticas variáveis, como FEFO/LIFO, são injetadas por composição, não espalhadas em condicionais.

---

## 6. Linguagem do negócio no código

A linguagem ubíqua aparece nos nomes das classes, métodos e estados.

| Linguagem do negócio | Código |
|---|---|
| Pedido | `Order` |
| Item de pedido | `OrderItem` |
| Produto | `Product` |
| Categoria de bebida | `BeverageCategory` |
| Lote | `Batch` |
| Estoque | `StockRegistry` |
| Movimentação de estoque | `StockMovement` |
| Entrada de estoque | `MovementType.INBOUND` |
| Saída de estoque | `MovementType.OUTBOUND` |
| Separação total | `TotalSeparation` |
| Política FEFO | `FefoBatchSelectionPolicy` |
| Expedição | `ship()` |
| Código de rastreio | `tracking_code` |
| Data de expedição | `shipped_at` |
| Pedido separado | `SEPARADO` |
| Pedido em transporte | `EM TRANSPORTE` |

A regra de nomenclatura adotada é: nomes em inglês no código, mas com correspondência direta aos termos de negócio usados nas aulas e nas discussões do projeto.

---

## 7. Proposta de evolução da modelagem profunda

A evolução recomendada para a entrega final é:

1. transformar `User` e `Role` em entidades reais.
2. criar política de autorização para ações críticas, como expedir pedido e cancelar pedido;
3. permitir múltiplos produtos por pedido no `OrderFactory` a partir do JSON;
4. criar repositórios simples para produtos e estoque, se o volume de dummy data crescer;
5. manter `OrderWorkflow` apenas como orquestrador, sem mover regras do domínio para ele.