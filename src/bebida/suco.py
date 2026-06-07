from dataclasses import dataclass
from .bebida import Bebida


@dataclass
class Suco(Bebida):
    """
    Representa um suco no catálogo da distribuidora.
    Adiciona atributos específicos como fruta base e percentual de polpa.
    """
    fruta: str = "Laranja"
    percentual_polpa: float = 100.0

    def __post_init__(self) -> None:
        super().__post_init__()
        if not (0.0 <= self.percentual_polpa <= 100.0):
            raise ValueError(
                f"Percentual de polpa inválido: {self.percentual_polpa}%. "
                "Deve estar entre 0% e 100%."
            )

    @property
    def categoria(self) -> str:
        return "Suco"

    def descricao_completa(self) -> str:
        return (
            f"[{self.categoria}] {self.nome} | Fruta: {self.fruta} | "
            f"Volume: {self.volume_ml}ml | "
            f"Preco: R$ {self.preco_unitario:.2f}"
        )
