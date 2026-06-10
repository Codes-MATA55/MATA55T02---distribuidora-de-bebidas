from typing import list

from domain.value_objects.item_pedido import ItemPedido
from domain.value_objects.dinheiro import Dinheiro

class Pedido:
    TRANSICOES_STATUS = {
        "AGUARDANDO PAGAMENTO": {
            "EM PROCESSAMENTO",
            "CANCELADO",
        },
        "EM PROCESSAMENTO": {
            "FINALIZADO",
            "CANCELADO",
            "ATRASADO",
            "EM TRANSPORTE",            
        },
        "ATRASADO": {
            "FINALIZADO",
            "CANCELADO"
        },
        "EM TRANSPORTE": {
            "FINALIZADO",
            "CANCELADO",
            "ATRASADO"
        },
        "FINALIZADO": {},
        "CANCELADO": {}
    }

    def __init__(self, id, id_cliente, produtos: list[ItemPedido]):
        self.id = id 
        self.id_cliente = id_cliente
        self.produtos = produtos
        self.status = "AGUARDANDO PAGAMENTO"
        self.total = self.calcular_total()

    def calcular_total(self):
        totais_produtos_dinheiro = [produto.calcular_subtotal() for produto in self.produtos]
        totais_produtos_centavos = [total.valor for total in totais_produtos_dinheiro]
        total_pedido_centavos = sum(totais_produtos_centavos)
        total_pedido_string = Dinheiro.converter_centavos_para_string(total_pedido_centavos)
        return Dinheiro(total_pedido_string)
    
    def atualizar_status(self, novo_status: str):
        status_atual = self.status
        if novo_status not in self.TRANSICOES_STATUS[status_atual]:
            raise ValueError(f"Não é permitido mudar de f{status_atual} para f{novo_status}")
        self.status = novo_status
    
    def adicionar_produto(self, item_pedido : ItemPedido):
        if not isinstance(item_pedido, ItemPedido):
            raise ValueError("Item inválido")        
        self.produtos.append(item_pedido)
        self.total = self.calcular_total()
    
    def remover_produto(self, id_produto):
        self.produtos = [item for item in self.produtos if item.id_produto != id_produto]
        self.total = self.calcular_total()

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
            
        return sum(item.quantidade for item in self.produtos)  
