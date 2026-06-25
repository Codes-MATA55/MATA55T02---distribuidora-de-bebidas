from datetime import datetime

from domain.entities.produto import Product
from domain.enums.tipo_movimentacao import MovementType
from domain.value_objects.ids import MovimentacaoId


class StockMovement:
    def __init__(self, product: Product, type: MovementType, amount: int, id: MovimentacaoId = None):
        if amount <= 0:
            raise ValueError("Quantidade da movimentação deve ser positiva")
        self.id = id or MovimentacaoId()
        self.product = product
        self.type = type
        self.amount = amount
        self.movement_date = datetime.now()
        self.update_stock()

    @property
    def data(self):
        return self.movement_date

    def update_stock(self):
        if self.type == MovementType.INBOUND:
            self.product.add_stock(self.amount)
        elif self.type == MovementType.OUTBOUND:
            self.product.remove_stock(self.amount)
