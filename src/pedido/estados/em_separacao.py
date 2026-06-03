from __future__ import annotations
from typing import TYPE_CHECKING
from .estado_pedido import EstadoPedido

if TYPE_CHECKING:
    from ..pedido import Pedido


class EmSeparacao(EstadoPedido):
    """
    Pedido está sendo separado no armazém.
    Permite: finalizar separação ou cancelar.
    """

    @property
    def nome(self) -> str:
        return "EmSeparacao"

    def finalizar_separacao(self, pedido: "Pedido") -> None:
        from .separado import Separado
        pedido._mudar_estado(Separado())

    def cancelar(self, pedido: "Pedido") -> None:
        from .cancelado import Cancelado
        pedido._mudar_estado(Cancelado())
