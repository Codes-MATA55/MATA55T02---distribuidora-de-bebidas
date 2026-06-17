from __future__ import annotations
from estoque.repository import EstoqueRepository
from estoque.value_objects import Quantidade
from pedido.aggregate import Pedido


class ServicoReservaEstoque:
    def __init__(self, estoque_repo: EstoqueRepository):
        self.__estoque_repo = estoque_repo

    def processar_reserva_para_pedido(self, pedido: Pedido) -> None:
        estoques_por_item = []

        for item in pedido.itens:
            estoque = self.__estoque_repo.buscar_por_produto(str(item.produto_id))
            if estoque is None:
                raise ValueError(
                    f"Estoque não encontrado para o produto '{item.produto_id}'."
                )
            qtd = Quantidade(item.quantidade)
            if not estoque.possui_disponibilidade(qtd):
                raise ValueError(
                    f"Estoque insuficiente para o produto '{item.produto_id}'. "
                    f"Disponível: {estoque.quantidade_disponivel}, Solicitado: {qtd}"
                )
            estoques_por_item.append((estoque, qtd))

        for estoque, qtd in estoques_por_item:
            estoque.reservar(qtd)
            self.__estoque_repo.salvar(estoque)
