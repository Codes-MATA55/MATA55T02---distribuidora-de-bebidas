from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from uuid import uuid4


@dataclass
class Bebida(ABC):
    """
    Abstração base para todas as bebidas da distribuidora.
    Encapsula atributos comuns e define o contrato para subclasses.
    """
    nome: str
    volume_ml: int
    preco_unitario: float
    id: str = field(default_factory=lambda: str(uuid4()))

    def __post_init__(self) -> None:
        self._validar()

    def _validar(self) -> None:
        if self.volume_ml <= 0:
            raise ValueError(f"Volume deve ser positivo. Recebido: {self.volume_ml}")
        if self.preco_unitario < 0:
            raise ValueError(f"Preço não pode ser negativo. Recebido: {self.preco_unitario}")
        if not self.nome or not self.nome.strip():
            raise ValueError("Nome da bebida não pode ser vazio.")

    @property
    @abstractmethod
    def categoria(self) -> str:
        """Retorna a categoria da bebida (ex: 'Cerveja', 'Refrigerante', 'Suco')."""
        ...

    @abstractmethod
    def descricao_completa(self) -> str:
        """Retorna uma descrição detalhada do produto."""
        ...

    def __repr__(self) -> str:
        return f"{self.categoria}(id={self.id!r}, nome={self.nome!r}, volume={self.volume_ml}ml)"
