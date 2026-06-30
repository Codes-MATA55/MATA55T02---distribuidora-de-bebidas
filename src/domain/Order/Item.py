from __future__ import annotations
from dataclasses import dataclass
from enum import Enum


class Product(Enum):
    BEER = "cerveja"
    SODA = "refrigerante"
    JUICE = "suco"


@dataclass(frozen=True)
class OrderItem:
    """Value Object: item de um pedido. Imutável e comparável por valor.
    Existe apenas no contexto de um Order — sem identidade própria nem ciclo
    de vida independente, por isso vive dentro do pacote domain/Order/.
    """
    product: Product
    quantity: int

    def __post_init__(self) -> None:
        if self.quantity <= 0:
            raise ValueError("Quantidade do item deve ser maior que zero.")
                
