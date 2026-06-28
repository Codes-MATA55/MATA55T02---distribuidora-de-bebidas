from __future__ import annotations
from abc import ABC, abstractmethod


class RoutingPort(ABC):
    @abstractmethod
    def best_route(self, stops: list[str]) -> list[str]:
        """Recebe as paradas de entrega e retorna a rota ordenada.

        Mantém a aplicação independente do provedor de roteirização. Trocar de
        provedor exige apenas outra implementação desta interface, sem impacto
        no domínio.
        """
