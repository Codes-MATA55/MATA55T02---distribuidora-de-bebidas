from __future__ import annotations
from typing import TYPE_CHECKING
from .estado_pedido import EstadoPedido

if TYPE_CHECKING:
    from ..pedido import Pedido


class Separado(EstadoPedido):
    """
    Pedido foi separado e está pronto para expedição.
    Permite: iniciar expedição.
    Não permite cancelamento (separação já feita).
    """

    @property
    def nome(self) -> str:
        return "Separado"

    def iniciar_expedicao(self, pedido: "Pedido") -> None:
        from .em_expedicao import EmExpedicao
        pedido._mudar_estado(EmExpedicao())
