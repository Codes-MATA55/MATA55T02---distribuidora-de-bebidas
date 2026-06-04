from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..pedido import Pedido


class EstadoPedido(ABC):
    """
    Interface base para o State Pattern do pedido.

    Cada estado concreto sabe:
    1. Qual é seu nome
    2. Quais transições são permitidas a partir dele
    3. Como executar cada transição

    Isso elimina ifs/elses espalhados e centraliza as regras
    de transição dentro de cada estado.
    """

    @property
    @abstractmethod
    def nome(self) -> str:
        """Nome legível do estado."""
        ...

    def iniciar_separacao(self, pedido: "Pedido") -> None:
        self._transicao_invalida("iniciar_separacao")

    def finalizar_separacao(self, pedido: "Pedido") -> None:
        self._transicao_invalida("finalizar_separacao")

    def iniciar_expedicao(self, pedido: "Pedido") -> None:
        self._transicao_invalida("iniciar_expedicao")

    def confirmar_entrega(self, pedido: "Pedido") -> None:
        self._transicao_invalida("confirmar_entrega")

    def cancelar(self, pedido: "Pedido") -> None:
        self._transicao_invalida("cancelar")

    def _transicao_invalida(self, operacao: str) -> None:
        from ...exceptions.regras_negocio import TransicaoDeEstadoInvalidaException
        raise TransicaoDeEstadoInvalidaException(self.nome, operacao)

    def __str__(self) -> str:
        return self.nome
