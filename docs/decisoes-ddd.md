| Entidade | Arquivo | Decisão |
|---|---|---|
| `Order` | `src/domain/entities/pedido.py` | Raiz do agregado de pedido; controla itens, status, separação, expedição e rastreio. |
| `Product` | `src/domain/entities/produto.py` | Identifica produto por ID/barcode, categoria, preço e estoque agregado. |
| `Batch` | `src/domain/entities/lote.py` | Representa lote físico com validade e quantidade própria. |
| `Fornecedor` | `src/domain/entities/fornecedor.py` | Cadastro mockado de fornecedor com CNPJ e contatos. |
| `StockMovement` | `src/domain/entities/movimentacao_estoque.py` | Registro identificável de entrada/saída de estoque. |

---

| Value Object | Arquivo | Decisão |
|---|---|---|
| `Quantity` | `src/domain/value_objects/quantidade.py` | Evita quantidades negativas e centraliza soma/subtração. |
| `ValidityWindow` | `src/domain/value_objects/faixa_validade.py` | Centraliza regra de validade de lote. |
| `Money` | `src/domain/value_objects/dinheiro.py` | Representa dinheiro em centavos e formato brasileiro. |
| `CPF`, `CNPJ`, `Email`, `PhoneNumber`, `Address` | `src/domain/value_objects/` | Protegem formatos e validações cadastrais. |
| `PedidoId`, `BatchId`, `ProdutoId`, etc. | `src/domain/value_objects/ids.py` | Identificadores imutáveis para entidades. |

---

`Order` protege:

- alteração de itens somente antes de pagamento;
- cálculo do total financeiro;
- quantidade física separada;
- transições de estado;
- expedição;
- rastreio.

`OrderItem` pertence ao agregado `Order` e não deve ser salvo ou manipulado isoladamente.

`StockRegistry` protege:

- lotes disponíveis;
- saldo por produto;
- baixa de estoque;
- histórico de movimentações.

`Batch` e `StockMovement` colaboram com `StockRegistry` para manter consistência do estoque.

---

Arquivo:

src/domain/factories.py


Factories existentes:

- `ProductFactory`
- `BatchFactory`
- `OrderFactory`

Decisão: factories criam objetos válidos a partir de `dummy_data.json`, evitando que `main.py` conheça detalhes de construção.

---

Arquivos:

src/domain/repositories/protocols.py
src/domain/repositories/in_memory_order_repository.py
src/domain/repositories/json_order_repository.py

Repositórios existentes:

- `InMemoryOrderRepository`: usado em testes e cenários sem arquivo;
- `JsonOrderRepository`: simula persistência em `orders.json`;
- `OrderRepository`: contrato usado pelo fluxo principal.

Decisão: a persistência é simulada, mas o domínio não depende diretamente de JSON.

---

`TotalSeparation` responsável por uma regra que envolve múltiplos objetos:

Order + OrderItem + StockRegistry + Batch + StockMovement

A separação total não pertence exclusivamente ao pedido nem exclusivamente ao estoque. Por isso foi modelada como serviço de domínio.

`OrderWorkflow` coordena o caso de uso:

confirmar pagamento → separar → expedir → salvar → notificar

Decisão: `OrderWorkflow` não decide regra de negócio; ele chama os objetos corretos.

---

| Invariante | Onde fica |
|---|---|
| Quantidade não pode ser negativa | `Quantity` |
| Lote não pode consumir mais do que possui | `Batch.consume_amount(...)` |
| Lote vencido não entra no saldo válido | `Batch.is_expired(...)` e `StockRegistry.valid_batches_for(...)` |
| Estoque não baixa acima do disponível | `StockRegistry.withdraw(...)` |
| Pedido não muda de status livremente | `Order.update_status(...)` |
| Pedido só fica separado com todos os itens separados | `Order.mark_as_separated()` |
| Pedido só expede depois de separado | `Order.ship()` |
| Pedido não expede duas vezes | `Order.ship()` |

---

Foram evitadas abstrações sem função prática. As abstrações criadas resolvem problemas reais:

- `OrderRepository`: permite JSON e memória sem mudar o fluxo;
- `BatchSelectionPolicy`: permite trocar a política de separação;
- `ShipmentNotifier`: simula integração externa sem acoplar o domínio;
- Factories: centralizam construção a partir de JSON.

Não foram criados frameworks, banco de dados, controllers, ORM nem camadas artificiais.