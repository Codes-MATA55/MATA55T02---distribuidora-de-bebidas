from datetime import datetime
from src.domain.produtos.produto import Produto
from src.domain.estoque.tipo_movimentacao import TipoMovimentacao


class MovimentacaoEstoque:
    def __init__(self, id: int, produto: Produto, tipo: TipoMovimentacao, quantidade: int):
        if quantidade <= 0:
            raise ValueError("Quantidade da movimentação deve ser positiva")
        self.id = id
        self.produto = produto
        self.tipo = tipo
        self.quantidade = quantidade
        self.data = datetime.now()
        self.atualizar_estoque()

    def atualizar_estoque(self):
        if self.tipo == TipoMovimentacao.ENTRADA:
            self.produto.adicionar_estoque(self.quantidade)
        elif self.tipo == TipoMovimentacao.SAIDA:
            self.produto.remover_estoque(self.quantidade)
