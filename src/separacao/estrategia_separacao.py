from abc import ABC, abstractmethod
from ..pedido.pedido import Pedido
from ..estoque.estoque import Estoque


class EstrategiaSeparacao(ABC):
    """
    Interface base para o Strategy Pattern de separação.

    A arquitetura permite que novas estratégias sejam adicionadas
    sem modificar o código existente (Princípio Aberto/Fechado).

    Estratégias planejadas:
    - FIFO (implementado)
    - LIFO (futuro)
    - Prioridade (futuro)
    - Urgente (futuro)
    """

    @abstractmethod
    def separar(self, pedido: Pedido, estoque: Estoque) -> None:
        """
        Executa a separação do pedido conforme a estratégia.
        Deve transicionar o pedido para o estado correto ao finalizar.
        """
        ...

    @property
    @abstractmethod
    def nome(self) -> str:
        """Nome descritivo da estratégia."""
        ...
