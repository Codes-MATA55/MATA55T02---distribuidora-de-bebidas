from pathlib import Path

from domain.entities.pedido import Order
from domain.json_storage import read_json, write_json

class JsonOrderRepository:
    def __init__(self, path: Path) -> None:
        self._path = path

    def save(self, order: Order) -> None:
        orders = self.list_all()
        snapshot = order.to_dict()
        orders = [item for item in orders if item.get("id") != snapshot["id"]]
        orders.append(snapshot)
        write_json(self._path, orders)

    def find_by_id(self, order_id: str) -> dict | None:
        for order in self.list_all():
            if order.get("id") == str(order_id):
                return order
        return None

    def list_all(self) -> list[dict]:
        return read_json(self._path, default=[])
    