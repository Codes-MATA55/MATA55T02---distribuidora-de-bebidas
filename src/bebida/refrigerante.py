from dataclasses import dataclass
from .bebida import Bebida


@dataclass
class Refrigerante(Bebida):
    """
    Representa um refrigerante no catálogo da distribuidora.
    Adiciona atributos específicos como sabor e se é zero.
    """
    sabor: str = "Coca"
    is_diet: bool = False

    @property
    def categoria(self) -> str:
        return "Refrigerante"

    def descricao_completa(self) -> str:
        return (
            f"[{self.categoria}] {self.nome} | "
            f"Sabor: {self.sabor} | "
            f"Volume: {self.volume_ml}ml | "
            f"Preco: R$ {self.preco_unitario:.2f}"
        )
