from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from uuid import UUID


class StatusPedido(Enum):
    RASCUNHO = "rascunho"
    CONFIRMADO = "confirmado"
    SEPARADO = "separado"
    EXPEDIDO = "expedido"
    CANCELADO = "cancelado"


@dataclass(frozen=True)
class ItemPedido:
    produto_id: UUID
    quantidade: int

    def __post_init__(self):
        if self.quantidade <= 0:
            raise ValueError(
                f"Quantidade do item deve ser positiva. Recebido: {self.quantidade}"
            )

    def __str__(self) -> str:
        return f"ItemPedido[produto={self.produto_id}, quantidade={self.quantidade}]"
