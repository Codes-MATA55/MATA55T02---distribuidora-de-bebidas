from typing import List

from domain.value_objects.dinheiro import Money
from domain.value_objects.ids import ClienteId, PedidoId
from domain.value_objects.item_pedido import OrderItem


class Order:
    TRANSITION_STATUS = {
        "AGUARDANDO PAGAMENTO": {
            "EM PROCESSAMENTO",
            "CANCELADO",
        },
        "EM PROCESSAMENTO": {
            "SEPARADO",
            "FINALIZADO",
            "CANCELADO",
            "ATRASADO",
            "EM TRANSPORTE",
        },
        "SEPARADO": {
            "FINALIZADO",
            "CANCELADO",
            "EM TRANSPORTE",
        },
        "ATRASADO": {
            "FINALIZADO",
            "CANCELADO",
        },
        "EM TRANSPORTE": {
            "FINALIZADO",
            "CANCELADO",
            "ATRASADO",
        },
        "FINALIZADO": set(),
        "CANCELADO": set(),
    }

    def __init__(self, items: List[OrderItem], id: PedidoId = None, client_id: ClienteId = None):
        self.id = id or PedidoId()
        self.client_id = client_id or ClienteId()
        self.items = items
        self.status = "AGUARDANDO PAGAMENTO"
        self.total = self.calculate_total()

    @property
    def produtos(self) -> List[OrderItem]:
        return self.items

    @produtos.setter
    def produtos(self, items: List[OrderItem]) -> None:
        self.items = items

    def calculate_total(self) -> Money:
        item_totals = [item.get_total() for item in self.items]
        total_cents = sum(total.value for total in item_totals)
        total_formatted = Money.convert_cents_to_string(total_cents)
        return Money(total_formatted)

    def update_status(self, new_status: str):
        current_status = self.status
        if new_status not in self.TRANSITION_STATUS[current_status]:
            raise ValueError(f"Não é permitido mudar de {current_status} para {new_status}")
        self.status = new_status

    def add_item(self, order_item: OrderItem):
        if not isinstance(order_item, OrderItem):
            raise ValueError("Item inválido")
        self.items.append(order_item)
        self.total = self.calculate_total()

    def add_product(self, order_item: OrderItem):
        self.add_item(order_item)

    def remove_item_by_product(self, removed_product_id):
        self.items = [item for item in self.items if item.product_id != removed_product_id]
        self.total = self.calculate_total()

    def remove_product(self, product_id):
        self.remove_item_by_product(product_id)

    def cancel_order(self):
        self.status = "CANCELADO"

    def end_order(self):
        self.status = "FINALIZADO"

    def get_separate_financial_total(self) -> Money:
        if self.status not in ["SEPARADO", "FINALIZADO"]:
            raise ValueError(
                f"Não é possível calcular o total separado. "
                f"O pedido está em estado: {self.status}"
            )

        return self.total

    def get_separate_physical_amount(self) -> int:
        if self.status not in ["SEPARADO", "FINALIZADO"]:
            raise ValueError(
                f"Não é possível obter a quantidade separada. "
                f"O pedido está em estado: {self.status}"
            )

        return sum(item.amount for item in self.items)
