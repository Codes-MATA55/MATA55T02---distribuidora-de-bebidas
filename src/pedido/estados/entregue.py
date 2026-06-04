from .estado_pedido import EstadoPedido


class Entregue(EstadoPedido):
    """
    Estado terminal de sucesso.
    Nenhuma transição é permitida a partir daqui.
    """

    @property
    def nome(self) -> str:
        return "Entregue"
