from __future__ import annotations
import uuid
from typing import List
from uuid import UUID

from pedido.value_objects import ItemPedido, StatusPedido


_TRANSICOES_VALIDAS = {
    StatusPedido.RASCUNHO: {StatusPedido.CONFIRMADO, StatusPedido.CANCELADO},
    StatusPedido.CONFIRMADO: {StatusPedido.SEPARADO, StatusPedido.CANCELADO},
    StatusPedido.SEPARADO: {StatusPedido.EXPEDIDO},
    StatusPedido.EXPEDIDO: set(),
    StatusPedido.CANCELADO: set(),
}


class Pedido:
    def __init__(self, id: str, usuario_id: str):
        self.__id = id
        self.__usuario_id = usuario_id
        self.__status = StatusPedido.RASCUNHO
        self.__itens: List[ItemPedido] = []

    @staticmethod
    def criar(usuario_id: str) -> Pedido:
        return Pedido(id=str(uuid.uuid4()), usuario_id=usuario_id)

    @property
    def id(self) -> str:
        return self.__id

    @property
    def usuario_id(self) -> str:
        return self.__usuario_id

    @property
    def status(self) -> StatusPedido:
        return self.__status

    @property
    def itens(self) -> List[ItemPedido]:
        return list(self.__itens)

    def adicionar_item(self, produto_id: UUID, quantidade: int) -> None:
        if self.__status != StatusPedido.RASCUNHO:
            raise ValueError(
                f"Não é possível adicionar itens a um pedido com status '{self.__status.value}'."
            )
        self.__itens.append(ItemPedido(produto_id=produto_id, quantidade=quantidade))

    def confirmar(self) -> None:
        if not self.__itens:
            raise ValueError("Pedido deve possuir pelo menos um item para ser confirmado.")
        self.__transicionar_para(StatusPedido.CONFIRMADO)

    def marcar_como_separado(self) -> None:
        self.__transicionar_para(StatusPedido.SEPARADO)

    def expedir(self) -> None:
        self.__transicionar_para(StatusPedido.EXPEDIDO)

    def cancelar(self) -> None:
        self.__transicionar_para(StatusPedido.CANCELADO)

    def __transicionar_para(self, novo_status: StatusPedido) -> None:
        if novo_status not in _TRANSICOES_VALIDAS[self.__status]:
            raise ValueError(
                f"Transição inválida: '{self.__status.value}' → '{novo_status.value}'."
            )
        self.__status = novo_status

    def __str__(self) -> str:
        return (
            f"Pedido[id={self.__id}, usuario={self.__usuario_id}, "
            f"status={self.__status.value}, itens={len(self.__itens)}]"
        )
