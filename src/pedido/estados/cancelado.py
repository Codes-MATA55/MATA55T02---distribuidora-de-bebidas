from .estado_pedido import EstadoPedido


class Cancelado(EstadoPedido):
    """
    Estado terminal de cancelamento.
    Nenhuma transição é permitida a partir daqui.
    """

    @property
    def nome(self) -> str:
        return "Cancelado"
