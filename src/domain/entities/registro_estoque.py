from typing import List
from domain.entities.movimentacao_estoque import MovimentacaoEstoque

class RegistroEstoque:
    def __init__(self):
        self._historico: List[MovimentacaoEstoque] = []

    def registrar(self, movimentacao: MovimentacaoEstoque):
        self._historico.append(movimentacao)

    def listar_historico(self) -> List[MovimentacaoEstoque]:
        return self._historico