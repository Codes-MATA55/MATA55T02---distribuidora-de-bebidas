from typing import Protocol

from domain.entities.pedido import Order


# ==================
# Atividade Avaliativa 2 : Commit 3 (Implementar contrato/protocolo)
# The domain flow depends on this contract instead of depending on JSON functions directly.
# ==================
class OrderRepository(Protocol):
    def save(self, order: Order) -> None:
        pass

    def find_by_id(self, order_id: str) -> dict | None:
        pass

    def list_all(self) -> list[dict]:
        pass
# ==================


class ShipmentNotifier(Protocol):
    def notify_shipped(self, order: Order) -> None:
        pass
      
