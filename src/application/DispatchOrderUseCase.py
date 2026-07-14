from __future__ import annotations

from application.AddressValidationPort import AddressValidationPort
from application.CarrierPort import CarrierPort
from application.RoutingPort import RoutingPort
from domain.Order.Repository import OrderRepository

class OrderNotFound(Exception):
    pass
   
class DispatchOrderUseCase:
  
    def __init__(
        self,
        orders: OrderRepository,
        carrier: CarrierPort,
        routing: RoutingPort,
        address_validation: AddressValidationPort,
    ) -> None:
        self.__orders = orders
        self.__carrier = carrier
        self.__routing = routing
        self.__address_validation = address_validation

    def execute(self, order_id: str, zip_code: str) -> str:
        order = self.__orders.find_by_id(order_id)
        if order is None:
            raise OrderNotFound(f"Pedido {order_id} não encontrado.")

        delivery_address = self.__address_validation.resolve(zip_code)
        self.__routing.best_route([delivery_address])

        # Regra de negócio (pedido precisa ter itens, status precisa ser CREATED etc.) vive inteiramente dentro de Order.dispatch()
        order.dispatch()
        self.__orders.save(order)

        return self.__carrier.dispatch(order_id=order.id)
