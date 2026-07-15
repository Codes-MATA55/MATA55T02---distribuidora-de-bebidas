from datetime import date
from domain.entities.pedido import Order
from domain.entities.registro_estoque import StockRegistry
from domain.entities.separacao_total import TotalSeparation
from domain.repositories.protocols import OrderRepository, ShipmentNotifier


class OrderWorkflow:
    def __init__(self, order_repository: OrderRepository, 
                 separation_service: TotalSeparation, 
                 shipment_notifier: ShipmentNotifier) -> None:
        self._order_repository = order_repository
        self._separation_service = separation_service
        self._shipment_notifier = shipment_notifier

    def confirm_separate_ship(self, order: Order, 
                              stock_registry: StockRegistry, 
                              reference_date: date | None = None) -> str:
        order.confirm_payment()
        self._separation_service.execute(order, 
                                         stock_registry = stock_registry, 
                                         reference_date = reference_date)
        tracking_code = order.ship()
        self._order_repository.save(order)
        self._shipment_notifier.notify_shipped(order)
        return tracking_code
    