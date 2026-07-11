from pathlib import Path

from domain.entities.pedido import Order
from domain.json_storage import read_json, write_json


# ==================
# Atividade Avaliativa 2 : Commit 1 (Identificar dependência concreta problemática)
# Before this adapter, main.py knew how to read and write the JSON file. Now the JSON detail
# is isolated behind the repository contract.
#
# Atividade Avaliativa 2 : Commit 4 (Adaptador ou política concreta 1)
# JsonOrderRepository is the concrete adapter for simulated persistence with JSON.
# ==================
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
# ==================

