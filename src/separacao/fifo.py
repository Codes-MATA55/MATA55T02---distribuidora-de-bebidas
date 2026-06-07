from .estrategia_separacao import EstrategiaSeparacao
from ..pedido.pedido import Pedido
from ..estoque.estoque import Estoque
from ..exceptions.regras_negocio import EstoqueInsuficienteException


class FIFOSeparacao(EstrategiaSeparacao):
    """
    Estrategia de separacao FIFO (First In, First Out).
    """

    @property
    def nome(self) -> str:
        return "FIFO"

    def separar(self, pedido: Pedido, estoque: Estoque) -> None:
        self._validar_disponibilidade(pedido, estoque)
        pedido.iniciar_separacao()

        for item in pedido.itens:
            estoque.saida(
                produto_id=item.produto_id,
                quantidade=item.quantidade,
                motivo="Separacao FIFO - Pedido " + pedido.id[:8],
            )

        pedido.finalizar_separacao()

    def _validar_disponibilidade(
        self, pedido: Pedido, estoque: Estoque
    ) -> None:
        for item in pedido.itens:
            if not estoque.tem_saldo_suficiente(
                item.produto_id, item.quantidade
            ):
                saldo = estoque.consultar_saldo(item.produto_id)
                raise EstoqueInsuficienteException(
                    produto_id=item.produto_id,
                    quantidade_solicitada=item.quantidade,
                    quantidade_disponivel=saldo,
                )
