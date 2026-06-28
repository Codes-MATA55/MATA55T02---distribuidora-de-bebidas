from __future__ import annotations

from domain.Order.Entity import Order
from domain.Order.Repository import OrderRepository


class PlaceOrderUseCase:
    def __init__(self, orders: OrderRepository) -> None:
        self.__orders = orders

    def execute(self, order_id: str) -> Order:
        order = Order(order_id)
        self.__orders.save(order)
        return order
