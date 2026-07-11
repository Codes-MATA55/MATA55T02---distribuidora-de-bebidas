from __future__ import annotations

import json
from pathlib import Path

from domain.Order.Entity import Order, OrderStatus
from domain.Order.Item import OrderItem, Product
from domain.Order.Repository import OrderRepository

class JsonFileOrderRepository(OrderRepository):
    def __init__(self, file_path: str | Path) -> None:
        self.__file_path = Path(file_path)
        if not self.__file_path.exists():
            self.__file_path.write_text("{}", encoding="utf-8")

    def save(self, order: Order) -> None:
        data = self.__read_all()
        data[order.id] = {
            "id": order.id,
            "status": order.status.value,
            "items": [
                {"product": item.product.value, "quantity": item.quantity}
                for item in order.items
            ],
        }
        self.__write_all(data)

    def find_by_id(self, order_id: str) -> Order | None:
        data = self.__read_all()
        raw = data.get(order_id)
        if raw is None:
            return None
        return self.__rehydrate(raw)

    def __rehydrate(self, raw: dict) -> Order:
        order = Order(raw["id"])
        for raw_item in raw["items"]:
            order.add_item(
                OrderItem(
                    product=Product(raw_item["product"]),
                    quantity=raw_item["quantity"],
                )
            )
        target_status = OrderStatus(raw["status"])
        if target_status in (OrderStatus.DISPATCHED, OrderStatus.DELIVERED):
            order.dispatch()
        if target_status is OrderStatus.DELIVERED:
            order.deliver()
        return order

    def __read_all(self) -> dict:
        content = self.__file_path.read_text(encoding="utf-8")
        return json.loads(content) if content else {}

    def __write_all(self, data: dict) -> None:
        self.__file_path.write_text(
            json.dumps(data, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
