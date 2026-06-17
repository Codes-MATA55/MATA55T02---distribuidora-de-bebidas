from typing import List

from domain.entities.movimentacao_estoque import MovimentacaoEstoque


class RegistroEstoque:
    def __init__(self):
        self._movimentacoes: List[MovimentacaoEstoque] = []

    def registrar(self, movimentacao: MovimentacaoEstoque):
        self._movimentacoes.append(movimentacao)

    def listar_historico(self) -> List[MovimentacaoEstoque]:
        return list(self._movimentacoes)
