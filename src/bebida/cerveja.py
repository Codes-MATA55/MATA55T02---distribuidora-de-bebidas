from dataclasses import dataclass
from .bebida import Bebida


@dataclass
class Cerveja(Bebida):
    """
    Representa uma cerveja no catalogo da distribuidora.
    """
    tipo: str = "Lager"

    @property
    def categoria(self) -> str:
        return "Cerveja"

    def descricao_completa(self) -> str:
        return (
            f"[{self.categoria}] {self.nome} | Tipo: {self.tipo} | "
            f"Volume: {self.volume_ml}ml | "
            f"Preco: R$ {self.preco_unitario:.2f}"
        )