from __future__ import annotations
from typing import TYPE_CHECKING
from .estado_pedido import EstadoPedido

if TYPE_CHECKING:
    from ..pedido import Pedido


class Criado(EstadoPedido):
    """
    Estado inicial de todo pedido.
    Permite: iniciar separação ou cancelar.
    """

    @property
    def nome(self) -> str:
        return "Criado"

    def iniciar_separacao(self, pedido: "Pedido") -> None:
        from .em_separacao import EmSeparacao
        pedido._mudar_estado(EmSeparacao())

    def cancelar(self, pedido: "Pedido") -> None:
        from .cancelado import Cancelado
        pedido._mudar_estado(Cancelado())
