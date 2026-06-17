from __future__ import annotations

from estoque.repository import EstoqueRepository
from estoque.value_objects import Quantidade
from pedido.aggregate import Pedido


class ServicoReservaEstoque:
    def __init__(self, estoque_repo: EstoqueRepository):
        self.__estoque_repo = estoque_repo

    def processar_reserva_para_pedido(self, pedido: Pedido) -> None:
        for item in pedido.itens:
            estoque = self.__estoque_repo.buscar_por_produto(str(item.produto_id))
            if estoque is None:
                raise ValueError(
                    f"Estoque não encontrado para o produto '{item.produto_id}'."
                )
            qtd = Quantidade(item.quantidade)
            estoque.reservar(qtd)
            self.__estoque_repo.salvar(estoque)
