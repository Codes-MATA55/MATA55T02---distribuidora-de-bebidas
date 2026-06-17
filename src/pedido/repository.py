from __future__ import annotations
from typing import Dict, Optional

from pedido.aggregate import Pedido


class PedidoRepository:
    def __init__(self):
        self._pedidos: Dict[str, Pedido] = {}

    def buscar_por_id(self, id: str) -> Optional[Pedido]:
        return self._pedidos.get(id)

    def salvar(self, pedido: Pedido) -> None:
        self._pedidos[pedido.id] = pedido
