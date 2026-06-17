from datetime import datetime

from domain.entities.produto import Produto
from domain.enums.tipo_movimentacao import TipoMovimentacao
from domain.value_objects.ids import MovimentacaoId


class MovimentacaoEstoque:
    def __init__(self, produto: Produto, tipo: TipoMovimentacao, quantidade: int, id: MovimentacaoId = None):
        if quantidade <= 0:
            raise ValueError("Quantidade da movimentação deve ser positiva")
        self.id = id or MovimentacaoId()
        self.produto = produto
        self.tipo = tipo
        self.quantidade = quantidade
        self.data_movimentacao = datetime.now()
        self.atualizar_estoque()

    @property
    def data(self):
        return self.data_movimentacao

    def atualizar_estoque(self):
        if self.tipo == TipoMovimentacao.ENTRADA:
            self.produto.adicionar_estoque(self.quantidade)
        elif self.tipo == TipoMovimentacao.SAIDA:
            self.produto.baixar_estoque(self.quantidade)
