from __future__ import annotations
import uuid

from estoque.value_objects import Quantidade


class Estoque:
    def __init__(self, id: str, produto_id: str):
        self.__id = id
        self.__produto_id = produto_id
        self.__quantidade_disponivel = Quantidade(0)
        self.__quantidade_reservada = Quantidade(0)

    @staticmethod
    def criar(produto_id: str) -> Estoque:
        return Estoque(id=str(uuid.uuid4()), produto_id=produto_id)

    @property
    def id(self) -> str:
        return self.__id

    @property
    def produto_id(self) -> str:
        return self.__produto_id

    @property
    def quantidade_disponivel(self) -> Quantidade:
        return self.__quantidade_disponivel

    @property
    def quantidade_reservada(self) -> Quantidade:
        return self.__quantidade_reservada

    def possui_disponibilidade(self, qtd: Quantidade) -> bool:
        return self.__quantidade_disponivel.valor >= qtd.valor

    def reservar(self, qtd: Quantidade) -> None:
        if not self.possui_disponibilidade(qtd):
            raise ValueError(
                f"Estoque insuficiente. Disponível: {self.__quantidade_disponivel}, Solicitado: {qtd}"
            )
        self.__quantidade_disponivel = Quantidade(self.__quantidade_disponivel.valor - qtd.valor)
        self.__quantidade_reservada = self.__quantidade_reservada.adicionar(qtd)

    def efetuar_baixa_da_reserva(self, qtd: Quantidade) -> None:
        if self.__quantidade_reservada.valor ==  qtd.valor:
            raise ValueError(
                f"Reserva com valor incompatível para baixa. Reservado: {self.__quantidade_reservada}, Solicitado: {qtd}"
            )
        self.__quantidade_reservada = Quantidade(self.__quantidade_reservada.valor - qtd.valor)

    def repor(self, qtd: Quantidade) -> None:
        self.__quantidade_disponivel = self.__quantidade_disponivel.adicionar(qtd)

    def __str__(self) -> str:
        return (
            f"Estoque[produto={self.__produto_id}] "
            f"disponivel={self.__quantidade_disponivel} "
            f"reservado={self.__quantidade_reservada}"
        )
