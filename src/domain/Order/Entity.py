from __future__ import annotations
from enum import Enum
from domain.Order.Item import OrderItem
from domain.Order.Exceptions import InvalidOrderTransition


class OrderStatus(Enum):
    CREATED = "created"
    DISPATCHED = "dispatched"
    DELIVERED = "delivered"


class Order:
    def __init__(self, id: str) -> None:
        self.__id = id
        self.__status = OrderStatus.CREATED
        self.__items: list[OrderItem] = []

    @property
    def id(self) -> str:
        return self.__id

    @property
    def status(self) -> OrderStatus:
        return self.__status

    @property
    def items(self) -> list[OrderItem]:
        return list(self.__items)  # cópia defensiva: ninguém muda a lista por fora

    def add_item(self, item: OrderItem) -> None:
        if self.__status is not OrderStatus.CREATED:
            raise InvalidOrderTransition(
                f"Não é possível adicionar item a um pedido com status {self.__status.value}."
            )
        self.__items.append(item)

    def remove_item(self, item: OrderItem) -> None:
        if self.__status is not OrderStatus.CREATED:
            raise InvalidOrderTransition(
                f"Não é possível remover item de um pedido com status {self.__status.value}."
            )
        self.__items.remove(item)

    def dispatch(self) -> None:
        if self.__status is not OrderStatus.CREATED:
            raise InvalidOrderTransition(
                f"Não é possível despachar um pedido com status {self.__status.value}."
            )
        if not self.__items:
            raise InvalidOrderTransition("Não é possível despachar um pedido sem itens.")
        self.__status = OrderStatus.DISPATCHED

    def deliver(self) -> None:
        if self.__status is not OrderStatus.DISPATCHED:
            raise InvalidOrderTransition(
                f"Não é possível entregar um pedido com status {self.__status.value}."
            )
        self.__status = OrderStatus.DELIVERED
        