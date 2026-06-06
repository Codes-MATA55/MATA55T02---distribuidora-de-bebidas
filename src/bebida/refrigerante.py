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
        variante = "ero" if self.is_diet else "Regular"
        return (
            f"[{self.categoria}] {self.nome} | Sabor: {self.sabor} | "
            f"Volume: {self.volume_ml}ml | "
            f"Preço: R$ {self.preco_unitario:.2f}"
        )
