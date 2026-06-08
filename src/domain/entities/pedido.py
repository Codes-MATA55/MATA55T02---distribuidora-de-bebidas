from ast import List

from domain.value_objects import item_produto;

class Pedido:
    def __init__(self, id, id_cliente, produtos: List[item_produto]):
        self.id = id
        self.id_cliente = id_cliente
        self.produtos = produtos
        self.status = "EM PROCESSAMENTO"
        self.total = self.calcular_total()

    def calcular_total(self):
        return sum(item.calcular_subtotal() for item in self.produtos)
    
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


    

        
     