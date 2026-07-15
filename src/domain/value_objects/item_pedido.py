from dataclasses import dataclass, field
from .dinheiro import Money


@dataclass(frozen=True)
class OrderItem:
    product_id: int
    amount: int
    unit_price_str: str
    unit_price: Money = field(init=False)
    separated_amount: int = field(default=0, init=False)

    def __post_init__(self):
        if not isinstance(self.product_id, int):
            raise ValueError("ID do produto inválido")

        if not isinstance(self.amount, int) or self.amount <= 0:
            raise ValueError("Quantidade inválida")
        
        object.__setattr__(self, "unit_price", Money(self.unit_price_str))        
    
    def get_total(self) -> Money:
        amount_cents = self.unit_price.value * self.amount
        amount_string = Money.convert_cents_to_string(amount_cents)

        return Money(amount_string)

    def mark_separated(self, amount: int) -> None:
        if amount <= 0:
            raise ValueError("Quantidade separada deve ser positiva")
        if self.separated_amount + amount > self.amount:
            raise ValueError("Quantidade separada não pode exceder a quantidade pedida")
        object.__setattr__(self, "separated_amount", self.separated_amount + amount)

    def is_fully_separated(self) -> bool:
        return self.separated_amount == self.amount
    