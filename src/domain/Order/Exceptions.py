from __future__ import annotations


class InvalidOrderTransition(Exception):
    """Lançada quando uma transição de estado viola a regra de
    negócio do pedido."""