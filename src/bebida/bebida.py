from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from uuid import uuid4


@dataclass
class Bebida(ABC):
    """
    Abstracao base para todas as bebidas da distribuidora.
    """
    nome: str
    volume_ml: int
    preco_unitario: float
    id: str = field(default_factory=lambda: str(uuid4()))

    def __post_init__(self) -> None:
        self._validar()

    def _validar(self) -> None:
        if self.volume_ml <= 0:
            raise ValueError(
                f"Volume deve ser positivo. Recebido: {self.volume_ml}"
            )
        if self.preco_unitario < 0:
            raise ValueError(
                f"Preco nao pode ser negativo. "
                f"Recebido: {self.preco_unitario}"
            )
        if not self.nome or not self.nome.strip():
            raise ValueError("Nome da bebida nao pode ser vazio.")

    @property
    @abstractmethod
    def categoria(self) -> str:
        ...

    @abstractmethod
    def descricao_completa(self) -> str:
        ...

    def __repr__(self) -> str:
        return (
            f"{self.categoria}("
            f"id={self.id!r}, "
            f"nome={self.nome!r}, "
            f"volume={self.volume_ml}ml)"
        )
