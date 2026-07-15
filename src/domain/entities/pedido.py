from datetime import datetime
from typing import List
from uuid import uuid4

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
            "CANCELADO",
            "ATRASADO",
        },
        "SEPARADO": {
            "EM TRANSPORTE",
            "CANCELADO",
        },
        "ATRASADO": {
            "CANCELADO",
        },
        "EM TRANSPORTE": {
            "FINALIZADO",
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
        self.shipped_at: datetime | None = None
        self.tracking_code: str | None = None

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

    def _ensure_items_can_change(self) -> None:
        if self.status != "AGUARDANDO PAGAMENTO":
            raise ValueError("Order items can only be changed before payment confirmation")

    def is_terminal(self) -> bool:
        return self.status in {"FINALIZADO", "CANCELADO"}

    def add_item(self, order_item: OrderItem):
        self._ensure_items_can_change()
        if not isinstance(order_item, OrderItem):
            raise ValueError("Item inválido")
        self.items.append(order_item)
        self.total = self.calculate_total()

    def add_product(self, order_item: OrderItem):
        self.add_item(order_item)

    def remove_item_by_product(self, removed_product_id):
        self._ensure_items_can_change()
        self.items = [item for item in self.items if item.product_id != removed_product_id]
        self.total = self.calculate_total()

    def remove_product(self, product_id):
        self.remove_item_by_product(product_id)

    def cancel_order(self):
        self.update_status("CANCELADO")

    def end_order(self):
        self.update_status("FINALIZADO")

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
        return sum(item.separated_amount for item in self.items)

    def confirm_payment(self) -> None:
        self.update_status("EM PROCESSAMENTO")

    def can_be_separated(self) -> bool:

        return self.status == "EM PROCESSAMENTO" and bool(self.items)

    def mark_as_separated(self) -> None:
        if not self.items:
            raise ValueError("Pedido sem itens não pode ser separado")
        if not all(item.is_fully_separated() for item in self.items):
            raise ValueError("Pedido não pode ser marcado como separado com itens pendentes")
        self.update_status("SEPARADO")

    def _generate_tracking_code(self) -> str:
        return f"TRK-{str(self.id)[:8].upper()}-{uuid4().hex[:6].upper()}"

    def ship(self) -> str:
        if self.shipped_at is not None:
            raise ValueError("Pedido já foi expedido")
        if self.status != "SEPARADO":
            raise ValueError("Pedido só pode ser expedido após separação total")

        self.tracking_code = self._generate_tracking_code()
        self.shipped_at = datetime.now()
        self.update_status("EM TRANSPORTE")
        return self.tracking_code

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "client_id": str(self.client_id),
            "status": self.status,
            "total": self.total.value_str,
            "items": [
                {
                    "product_id": item.product_id,
                    "amount": item.amount,
                    "unit_price": item.unit_price.value_str,
                    "separated_amount": item.separated_amount,
                }
                for item in self.items
            ],
            "shipped_at": self.shipped_at.isoformat() if self.shipped_at else None,
            "tracking_code": self.tracking_code,
        }
