from dataclasses import dataclass
from ..bebida.bebida import Bebida


@dataclass(frozen=True)
class ItemPedido:
    """
    Representa um item dentro de um pedido.
    É imutável (frozen) para proteger a integridade do pedido.
    """
    produto_id: str
    bebida: Bebida
    quantidade: int

    def __post_init__(self) -> None:
        if self.quantidade <= 0:
            raise ValueError(
                f"Quantidade deve ser positiva. Recebido: {self.quantidade}"
            )

    @property
    def valor_total(self) -> float:
        return self.bebida.preco_unitario * self.quantidade

    def __str__(self) -> str:
        return (
            f"{self.bebida.nome} x{self.quantidade} "
            f"= R$ {self.valor_total:.2f}"
        )
