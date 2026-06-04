from __future__ import annotations
from typing import TYPE_CHECKING
from .estado_pedido import EstadoPedido

if TYPE_CHECKING:
    from ..pedido import Pedido


class EmExpedicao(EstadoPedido):
    """
    Pedido saiu para entrega.
    Permite: confirmar entrega.
    """

    @property
    def nome(self) -> str:
        return "EmExpedicao"

    def confirmar_entrega(self, pedido: "Pedido") -> None:
        from .entregue import Entregue
        pedido._mudar_estado(Entregue())
