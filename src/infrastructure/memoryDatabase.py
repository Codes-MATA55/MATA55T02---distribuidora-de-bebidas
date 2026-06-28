from __future__ import annotations

from domain.Order.Entity import Order
from domain.Order.Repository import OrderRepository


class MemoryDatabase(OrderRepository):
    def __init__(self) -> None:
        self.__orders: dict[str, Order] = {}

    def save(self, order: Order) -> None:
        self.__orders[order.id] = order

    def find_by_id(self, order_id: str) -> Order | None:
        return self.__orders.get(order_id)
