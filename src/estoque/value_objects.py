from __future__ import annotations
from dataclasses import dataclass
from enum import Enum


class TipoProduto(Enum):
    CERVEJA = "cerveja"
    REFRIGERANTE = "refrigerante"
    SUCO = "suco"


@dataclass(frozen=True)
class Quantidade:
    valor: int

    def __post_init__(self):
        if self.valor < 0:
            raise ValueError(f"Quantidade não pode ser negativa. Recebido: {self.valor}")

    def adicionar(self, outra: Quantidade) -> Quantidade:
        return Quantidade(self.valor + outra.valor)

    def subtrair(self, outra: Quantidade) -> Quantidade:
        return Quantidade(self.valor - outra.valor)  # validação de negativo já cobre underflow

    def __eq__(self, outra: object) -> bool:
        if not isinstance(outra, Quantidade):
            return NotImplemented
        return self.valor == outra.valor

    def __str__(self) -> str:
        return str(self.valor)
