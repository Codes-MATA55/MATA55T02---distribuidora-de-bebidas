from domain.entities.pedido import Order


class MemoryShipmentNotifier:
    def __init__(self) -> None:
        self.messages: list[str] = []

    def notify_shipped(self, order: Order) -> None:
        self.messages.append(
            f"Order {order.id} shipped with tracking code {order.tracking_code}"
        )


class ConsoleShipmentNotifier:
    def notify_shipped(self, order: Order) -> None:
        print(f"Order {order.id} shipped with tracking code {order.tracking_code}")
