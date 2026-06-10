from ast import List

from domain.value_objects.item_pedido import ItemPedido;
from domain.value_objects.dinheiro import Dinheiro;

class Pedido:
    def __init__(self, id, id_cliente, produtos: List[ItemPedido]):
        self.id = id 
        self.id_cliente = id_cliente
        self.produtos = produtos
        self.status = "EM PROCESSAMENTO"
        self.total = self.calcular_total()

    def calcular_total(self):
        valores = [produto.calcular_subtotal().valor for produto in self.produtos]
        total_centavos = sum(valores)
        total_str = Dinheiro.converter_centavos_para_string(total_centavos)
        return Dinheiro(total_str)
    
    def atualizar_status(self, novo_status):
        self.status = novo_status
    
    def adicionar_produto(self, item_produto):
        self.produtos.append(item_produto)
        self.total = self.calcular_total()
    
    def remover_produto(self, id_produto):
        self.produtos = [item for item in self.produtos if item.id_produto != id_produto]
        self.total = self.calcular_total()

    def cancelar_pedido(self):
        self.status = "CANCELADO"
        
    def finalizar_pedido(self):
        self.status = "FINALIZADO"


    

        
     