from domain.entities.pedido import Order


# ==================
# Atividade Avaliativa 1 : Commit 6 (Implementar repository simples)
# InMemoryOrderRepository stores order snapshots for tests and demos without using a database.
# ==================
class InMemoryOrderRepository:
    def __init__(self) -> None:
        self._orders: dict[str, dict] = {}

    def save(self, order: Order) -> None:
        self._orders[str(order.id)] = order.to_dict()

    def find_by_id(self, order_id: str) -> dict | None:
        order = self._orders.get(str(order_id))
        return dict(order) if order else None

    def list_all(self) -> list[dict]:
        return [dict(order) for order in self._orders.values()]
# ==================
