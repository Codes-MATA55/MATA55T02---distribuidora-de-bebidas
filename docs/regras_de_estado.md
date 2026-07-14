| Estado | Significado |
|---|---|
| `AGUARDANDO PAGAMENTO` | Pedido criado, ainda sem confirmação. Itens ainda podem ser alterados. |
| `EM PROCESSAMENTO` | Pedido confirmado e pronto para separação. |
| `SEPARADO` | Todos os itens foram separados fisicamente. |
| `EM TRANSPORTE` | Pedido expedido e com rastreio gerado. |
| `ATRASADO` | Pedido teve problema operacional após processamento/transporte. |
| `FINALIZADO` | Pedido encerrado após transporte. |
| `CANCELADO` | Pedido encerrado por cancelamento. |

---

| Origem | Destino permitido |
|---|---|
| `AGUARDANDO PAGAMENTO` | `EM PROCESSAMENTO`, `CANCELADO` |
| `EM PROCESSAMENTO` | `SEPARADO`, `CANCELADO`, `ATRASADO` |
| `SEPARADO` | `EM TRANSPORTE`, `CANCELADO` |
| `ATRASADO` | `CANCELADO` |
| `EM TRANSPORTE` | `FINALIZADO`, `ATRASADO` |
| `FINALIZADO` | Nenhuma transição |
| `CANCELADO` | Nenhuma transição |

---

| Ação do negócio | Método | Regra |
|---|---|---|
| Confirmar pagamento | `Order.confirm_payment()` | Só permite `AGUARDANDO PAGAMENTO → EM PROCESSAMENTO`. |
| Marcar como separado | `Order.mark_as_separated()` | Exige todos os itens completamente separados. |
| Expedir pedido | `Order.ship()` | Exige pedido em `SEPARADO`, gera rastreio e data. |
| Cancelar pedido | `Order.cancel_order()` | Usa `update_status("CANCELADO")`, respeitando transições. |
| Finalizar pedido | `Order.end_order()` | Usa `update_status("FINALIZADO")`, respeitando transições. |

---

A implementação deve bloquear:

- expedir pedido antes da separação;
- expedir pedido duas vezes;
- marcar como separado com item pendente;
- pular de `AGUARDANDO PAGAMENTO` direto para `SEPARADO`;
- finalizar pedido antes de estar em transporte;
- cancelar pedido já finalizado.

Essas regras estão cobertas em `tests/domain/test_transicoes_invalidas.py`.

---


Arquivo principal:

```text
src/domain/entities/pedido.py
```

Métodos principais:

```text
Order.update_status(...)
Order.confirm_payment()
Order.mark_as_separated()
Order.ship()
```

Decisão: `OrderWorkflow` coordena o fluxo, mas quem protege as transições é `Order`.
