from dataclasses import dataclass, field
from .dinheiro import Dinheiro


@dataclass(frozen=True)
class ItemPedido:
    product_id: int
    amount: int
    unit_price_str: str
    unit_price: Dinheiro = field(init=False)

    def __post_init__(self):
        if not isinstance(self.product_id, int):
            raise ValueError("ID do produto inválido")

        if not isinstance(self.amount, int) or self.amount <= 0:
            raise ValueError("amount inválida")
        
        object.__setattr__(self, "unit_price", Dinheiro(self.unit_price_str))        
    
    def calcular_subtotal(self) -> Dinheiro:
        amount_cents = self.unit_price.value * self.amount
        amount_string = Dinheiro.convert_cents_to_string(amount_cents)

        return Dinheiro(amount_string)