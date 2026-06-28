from __future__ import annotations
from abc import ABC, abstractmethod

from domain.Order.Entity import Order


class OrderRepository(ABC):
    @abstractmethod
    def save(self, order: Order) -> None:
        """Persiste a order no mecanismo de armazenamento da implementação.

        Contrato declarado no domínio para que a infraestrutura se submeta a ele
        (Dependency Inversion). O domínio não conhece banco nem framework; apenas
        exige esta interface.
        """

    @abstractmethod
    def find_by_id(self, order_id: str) -> Order | None:
        """Retorna a order com o id informado, ou None se não existir.

        Parte do contrato de persistência que o domínio impõe à infraestrutura,
        mantendo o domínio agnóstico de detalhes de armazenamento.
        """
