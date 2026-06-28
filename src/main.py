from __future__ import annotations

from application.PlaceOrderUseCase import PlaceOrderUseCase
from infrastructure.memoryDatabase import MemoryDatabase


def main() -> None:
    orders = MemoryDatabase()
    place_order = PlaceOrderUseCase(orders)

    order = place_order.execute(order_id="order-1")
    print(f"Order criada e persistida: {order.id}")
    print(f"Recuperada do repositorio: {orders.find_by_id('order-1').id}")


if __name__ == "__main__":
    main()
