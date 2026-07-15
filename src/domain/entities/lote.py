from datetime import date
from domain.entities.produto import Product
from domain.value_objects.ids import BatchId


class Batch:
    def __init__(self, product: Product, initial_amount: int, expiration_date: date, id: BatchId = None):
        if initial_amount <= 0:
            raise ValueError("A amount inicial do lote deve ser maior que zero")
        if not isinstance(expiration_date, date):
            raise ValueError("A data de validade deve ser um objeto válido do tipo date")
        
        self._id = id or BatchId()
        self._product = product
        self._initial_amount = initial_amount
        self._current_amount = initial_amount
        self._expiration_date = expiration_date

    @property
    def id(self) -> int:
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
        # Verifica se o lote está vencido com base em uma data de referência (padrão: hoje).
        if reference_date is None:
            reference_date = date.today()
        return self._expiration_date < reference_date

    def consume_amount(self, amount: int):
        # Consome uma quantidade do lote garantindo que não fique negativa.
        if amount <= 0:
            raise ValueError("A quantidade a ser consumida deve ser maior que zero")
        if amount > self._current_amount:
            raise ValueError(
                f"Saldo insuficiente no lote {self._id}. "
                f"Disponível: {self._current_amount}, Solicitado: {amount}"
            )
        self._current_amount -= amount
    
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
