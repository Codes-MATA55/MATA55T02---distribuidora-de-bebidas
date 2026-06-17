from typing import List

from domain.value_objects.dinheiro import Dinheiro
from domain.value_objects.ids import ClienteId, PedidoId
from domain.value_objects.item_pedido import ItemPedido


class Pedido:
    TRANSICOES_STATUS = {
        "AGUARDANDO PAGAMENTO": {
            "EM PROCESSAMENTO",
            "CANCELADO",
        },
        "EM PROCESSAMENTO": {
            "SEPARADO",
            "FINALIZADO",
            "CANCELADO",
            "ATRASADO",
            "EM TRANSPORTE",
        },
        "SEPARADO": {
            "FINALIZADO",
            "CANCELADO",
            "EM TRANSPORTE",
        },
        "ATRASADO": {
            "FINALIZADO",
            "CANCELADO",
        },
        "EM TRANSPORTE": {
            "FINALIZADO",
            "CANCELADO",
            "ATRASADO",
        },
        "FINALIZADO": set(),
        "CANCELADO": set(),
    }

    def __init__(self, itens: List[ItemPedido], id: PedidoId = None, id_cliente: ClienteId = None):
        self.id = id or PedidoId()
        self.id_cliente = id_cliente or ClienteId()
        self.itens = itens
        self.status = "AGUARDANDO PAGAMENTO"
        self.total = self.calcular_total()

    @property
    def produtos(self) -> List[ItemPedido]:
        return self.itens

    @produtos.setter
    def produtos(self, itens: List[ItemPedido]) -> None:
        self.itens = itens

    def calcular_total(self) -> Dinheiro:
        subtotais = [item.calcular_subtotal() for item in self.itens]
        total_centavos = sum(subtotal.valor for subtotal in subtotais)
        total_formatado = Dinheiro.converter_centavos_para_string(total_centavos)
        return Dinheiro(total_formatado)

    def atualizar_status(self, novo_status: str):
        status_atual = self.status
        if novo_status not in self.TRANSICOES_STATUS[status_atual]:
            raise ValueError(f"Não é permitido mudar de {status_atual} para {novo_status}")
        self.status = novo_status

    def adicionar_item(self, item_pedido: ItemPedido):
        if not isinstance(item_pedido, ItemPedido):
            raise ValueError("Item inválido")
        self.itens.append(item_pedido)
        self.total = self.calcular_total()

    def adicionar_produto(self, item_pedido: ItemPedido):
        self.adicionar_item(item_pedido)

    def remover_item_por_produto(self, id_produto):
        self.itens = [item for item in self.itens if item.id_produto != id_produto]
        self.total = self.calcular_total()

    def remover_produto(self, id_produto):
        self.remover_item_por_produto(id_produto)

    def cancelar_pedido(self):
        self.status = "CANCELADO"

    def finalizar_pedido(self):
        self.status = "FINALIZADO"

    def obter_total_financeiro_separado(self) -> Dinheiro:
        if self.status not in ["SEPARADO", "FINALIZADO"]:
            raise ValueError(
                f"Não é possível calcular o total separado. "
                f"O pedido está em estado: {self.status}"
            )

        return self.total

    def obter_quantidade_fisica_separada(self) -> int:
        if self.status not in ["SEPARADO", "FINALIZADO"]:
            raise ValueError(
                f"Não é possível obter a quantidade separada. "
                f"O pedido está em estado: {self.status}"
            )

        return sum(item.quantidade for item in self.itens)
