from .estrategia_separacao import EstrategiaSeparacao
from ..pedido.pedido import Pedido
from ..estoque.estoque import Estoque
from ..exceptions.regras_negocio import EstoqueInsuficienteException


class FIFOSeparacao(EstrategiaSeparacao):
    """
    Estratégia de separação FIFO (First In, First Out).

    Os produtos são separados na ordem em que foram adicionados ao pedido,
    reservando os itens mais antigos do estoque primeiro.

    Esta é a estratégia padrão da distribuidora.
    """

    @property
    def nome(self) -> str:
        return "FIFO"

    def separar(self, pedido: Pedido, estoque: Estoque) -> None:
        """
        1. Verifica se todos os itens têm saldo no estoque
        2. Reserva os itens na ordem de entrada (FIFO)
        3. Transiciona o pedido para EmSeparacao → Separado
        """
        self._validar_disponibilidade(pedido, estoque)
        pedido.iniciar_separacao()

        # Processa itens na ordem de chegada (FIFO)
        for item in pedido.itens:
            estoque.saida(
                produto_id=item.produto_id,
                quantidade=item.quantidade,
                motivo=f"Separação FIFO - Pedido {pedido.id[:8]}",
            )
            print(
                f"Separado: {item.bebida.nome} x{item.quantidade} "
                f"(FIFO | Pedido {pedido.id[:8]})"
            )

        pedido.finalizar_separacao()
        print(f"Pedido {pedido.id[:8]} separado com sucesso via FIFO.")

    def _validar_disponibilidade(self, pedido: Pedido, estoque: Estoque) -> None:
        """Valida antecipadamente todos os itens antes de iniciar a separação."""
        erros = []
        for item in pedido.itens:
            if not estoque.tem_saldo_suficiente(item.produto_id, item.quantidade):
                saldo = estoque.consultar_saldo(item.produto_id)
                erros.append(
                    f"'{item.bebida.nome}': solicitado {item.quantidade}, disponível {saldo}"
                )
        if erros:
            raise EstoqueInsuficienteException(
                produto_id="múltiplos",
                quantidade_solicitada=0,
                quantidade_disponivel=0,
            )
