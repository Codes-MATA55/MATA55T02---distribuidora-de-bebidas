Antes:

O risco inicial era concentrar no `main.py` responsabilidades como:

ler JSON
montar objetos
separar pedido
expedir pedido
salvar pedido
notificar expedição
escolher lotes

Problemas desse desenho:

- `main.py` ficaria procedural;
- regras de negócio poderiam ir para infraestrutura;
- testes dependeriam de arquivo JSON;
- trocar a política de lote exigiria alterar código de estoque/separação;
- simular notificação exigiria mexer no fluxo principal.

---

Depois:

O fluxo foi organizado assim:

main.py
  → factories
  → OrderWorkflow
      → OrderRepository protocol
          → JsonOrderRepository
          → InMemoryOrderRepository
      → ShipmentNotifier protocol
          → MemoryShipmentNotifier
          → ConsoleShipmentNotifier
      → TotalSeparation
          → BatchSelectionPolicy protocol
              → FefoBatchSelectionPolicy
              → LifoBatchSelectionPolicy

---

`OrderWorkflow` recebe:

OrderRepository
TotalSeparation
ShipmentNotifier

Ele não precisa saber se o pedido será salvo em JSON, memória ou outro meio futuro.

`TotalSeparation` recebe uma `BatchSelectionPolicy`.

Ele não precisa saber se a ordem será FEFO, LIFO ou outra política futura.

---

A injeção acontece no `main.py`:

repository = JsonOrderRepository(ORDERS_FILE)
notifier = MemoryShipmentNotifier()
separation_service = TotalSeparation(FefoBatchSelectionPolicy())
workflow = OrderWorkflow(repository, separation_service, notifier)

Decisão: não foi usado framework de DI porque o projeto é pequeno e acadêmico. A composição manual é suficiente e mais clara.

---

Contrato:

BatchSelectionPolicy

Implementações:

FefoBatchSelectionPolicy
LifoBatchSelectionPolicy

A ordem de consumo de lotes é um ponto que tende a variar. A regra padrão da distribuidora é FEFO, pois bebidas têm validade. Porém, ao isolar a política, o sistema pode testar ou substituir a estratégia sem alterar `StockRegistry` nem `TotalSeparation`.

---

Antes, a persistência poderia estar diretamente em `main.py`.

Depois, ficou em:

src/domain/json_storage.py
src/domain/repositories/json_order_repository.py

A notificação foi isolada por protocolo:

ShipmentNotifier

Implementações:

MemoryShipmentNotifier
ConsoleShipmentNotifier

Assim, uma integração real de e-mail, API ou fila poderia ser adicionada futuramente sem alterar `Order` ou `TotalSeparation`.

---

Com as abstrações, os testes podem usar:

InMemoryOrderRepository
MemoryShipmentNotifier
LifoBatchSelectionPolicy
FefoBatchSelectionPolicy

Benefícios:

- testes não dependem de arquivo real;
- políticas podem ser testadas isoladamente;
- fluxo de expedição pode ser validado sem console/API;
- persistência JSON pode ser testada como adaptador.

---

O acoplamento foi reduzido sem exagero arquitetural. O sistema continua simples, mas as partes que variam foram isoladas:

- persistência: repository;
- notificação: notifier;
- seleção de lotes: policy;
- caso de uso: workflow.

As regras de negócio continuam dentro dos objetos do domínio.