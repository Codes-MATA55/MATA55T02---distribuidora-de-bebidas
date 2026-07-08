from __future__ import annotations
from application.PlaceOrderUseCase import PlaceOrderUseCase
from infrastructure.memoryDatabase import MemoryDatabase
from domain.Order.Item import OrderItem, Product


def main() -> None:
    orders = MemoryDatabase()
    place_order = PlaceOrderUseCase(orders)

    order = place_order.execute(order_id="order-1")
    print(f"Order criada e persistida: {order.id}")
    print(f"Recuperada do repositorio: {orders.find_by_id('order-1').id}")
    print(f"Status inicial: {order.status}")

    order.add_item(OrderItem(product=Product.BEER, quantity=10000))
    order.add_item(OrderItem(product=Product.SODA, quantity=6000))
    order.add_item(OrderItem(product=Product.JUICE, quantity=40000))
    print(f"Itens: {order.items}")

    order.dispatch()
    print(f"Status após despacho: {order.status}")

    order.deliver()
    print(f"Status após entrega: {order.status}")


if __name__ == "__main__":
    main()