from datetime import date
from domain.entities.produto import Product
from domain.value_objects.faixa_validade import ValidityWindow
from domain.value_objects.ids import BatchId
from domain.value_objects.quantidade import Quantity


class Batch:
    def __init__(self, 
                 product: Product,
                 initial_amount: int, 
                 expiration_date: date, id: BatchId = None):

        initial_quantity = Quantity.positive(initial_amount)
        validity_window = ValidityWindow(expiration_date)

        self._id = id or BatchId()
        self._product = product
        self._initial_amount = initial_quantity.value
        self._current_amount = initial_quantity.value
        self._validity_window = validity_window
        self._expiration_date = validity_window.expiration_date

    @property
    def id(self) -> BatchId:
        return self._id

    @property
    def product(self) -> Product:
        return self._product

    @property
    def initial_amount(self) -> int:
        return self._initial_amount

    @property
    def current_amount(self) -> int:
        return self._current_amount

    @property
    def expiration_date(self) -> date:
        return self._expiration_date

    def is_expired(self, reference_date: date = None) -> bool:
        return self._validity_window.is_expired(reference_date)

    def consume_amount(self, amount: int):
        quantity = Quantity.positive(amount)
        if quantity.value > self._current_amount:
            raise ValueError(
                f"Saldo insuficiente no lote {self._id}. "
                f"Disponível: {self._current_amount}, Solicitado: {quantity.value}"
            )
        self._current_amount = Quantity(self._current_amount).subtract(quantity).value

    def can_supply(self, amount: int, reference_date: date = None) -> bool:
        return not self.is_expired(reference_date) and self.current_amount >= amount

    def to_dict(self) -> dict:
        return {
            "id": str(self.id),
            "product_id": self.product.id,
            "initial_amount": self.initial_amount,
            "current_amount": self.current_amount,
            "expiration_date": self.expiration_date.isoformat(),
        }
