from abc import ABC, abstractmethod
from ..pedido.pedido import Pedido
from ..estoque.estoque import Estoque


class EstrategiaSeparacao(ABC):
    """
    Interface base para o Strategy Pattern de separacao.
    A arquitetura permite que novas estrategias sejam adicionadas
    sem modificar o codigo existente (Principio Aberto/Fechado).
    Estrategias planejadas:
    - FIFO (implementado)
    - LIFO (futuro)
    - Prioridade (futuro)
    - Urgente (futuro)
    """

    @abstractmethod
    def separar(self, pedido: Pedido, estoque: Estoque) -> None:
        """
        Executa a separacao do pedido conforme a estrategia.
        """
        ...

    @property
    @abstractmethod
    def nome(self) -> str:
        """Nome descritivo da estrategia."""
        ...
