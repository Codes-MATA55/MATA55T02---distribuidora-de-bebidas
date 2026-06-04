from __future__ import annotations
from dataclasses import dataclass, field
from datetime import datetime
from uuid import uuid4
from typing import Optional

from .item_pedido import ItemPedido
from .estados.estado_pedido import EstadoPedido
from .estados.criado import Criado
from ..observadores.observer import EventBus, Evento


@dataclass
class Pedido:
    """
    Agregado raiz do domínio de pedidos.

    Responsabilidades:
    - Gerenciar seu ciclo de vida através do State Pattern
    - Proteger regras de negócio (ex: não permite setters de status)
    - Publicar eventos de domínio via EventBus
    - Manter a coleção de itens com integridade

    Convenção: métodos prefixados com _ são para uso interno
    (ex: _mudar_estado é chamado pelos estados, não pelo código externo).
    """

    cliente: str
    event_bus: Optional[EventBus] = field(default=None, repr=False)
    id: str = field(default_factory=lambda: str(uuid4()))
    criado_em: datetime = field(default_factory=datetime.now)
    _estado: EstadoPedido = field(default_factory=Criado, init=False, repr=False)
    _itens: list[ItemPedido] = field(default_factory=list, init=False, repr=False)
    _historico_estados: list[str] = field(default_factory=list, init=False, repr=False)

    def __post_init__(self) -> None:
        self._historico_estados.append(self._estado.nome)

    # -------------------------------------------------------------------------
    # Interface pública de leitura
    # -------------------------------------------------------------------------

    @property
    def estado_atual(self) -> str:
        return self._estado.nome

    @property
    def itens(self) -> list[ItemPedido]:
        return list(self._itens)

    @property
    def historico_estados(self) -> list[str]:
        return list(self._historico_estados)

    @property
    def valor_total(self) -> float:
        return sum(item.valor_total for item in self._itens)

    # -------------------------------------------------------------------------
    # Gerenciamento de itens
    # -------------------------------------------------------------------------

    def adicionar_item(self, item: ItemPedido) -> None:
        """Adiciona um item ao pedido. Só permitido no estado Criado."""
        if self._estado.nome != "Criado":
            raise ValueError(
                f"Não é possível adicionar itens a um pedido no estado '{self._estado.nome}'."
            )
        self._itens.append(item)

    # -------------------------------------------------------------------------
    # Transições de estado (interface pública de negócio)
    # Nenhuma dessas operações expõe ou seta o estado diretamente.
    # -------------------------------------------------------------------------

    def iniciar_separacao(self) -> None:
        """Inicia o processo de separação do pedido."""
        if not self._itens:
            raise ValueError("Não é possível iniciar separação de um pedido sem itens.")
        self._estado.iniciar_separacao(self)

    def finalizar_separacao(self) -> None:
        """Marca o pedido como completamente separado."""
        self._estado.finalizar_separacao(self)
        self._publicar_evento("PEDIDO_SEPARADO")

    def iniciar_expedicao(self) -> None:
        """Inicia o processo de expedição do pedido."""
        self._estado.iniciar_expedicao(self)
        self._publicar_evento("PEDIDO_EM_EXPEDICAO")

    def confirmar_entrega(self) -> None:
        """Confirma que o pedido foi entregue ao cliente."""
        self._estado.confirmar_entrega(self)
        self._publicar_evento("PEDIDO_ENTREGUE")

    def cancelar(self) -> None:
        """Cancela o pedido."""
        self._estado.cancelar(self)
        self._publicar_evento("PEDIDO_CANCELADO")

    # -------------------------------------------------------------------------
    # Métodos internos (convenção de uso pelo State Pattern)
    # -------------------------------------------------------------------------

    def _mudar_estado(self, novo_estado: EstadoPedido) -> None:
        """
        Chamado pelos estados concretos para efetuar a transição.
        Prefixo _ indica que não deve ser chamado externamente.
        """
        self._estado = novo_estado
        self._historico_estados.append(novo_estado.nome)

    def _publicar_evento(self, tipo: str) -> None:
        if self.event_bus:
            evento = Evento(
                tipo=tipo,
                dados={
                    "pedido_id": self.id,
                    "cliente": self.cliente,
                    "estado": self._estado.nome,
                    "itens": [
                        {"produto_id": i.produto_id, "quantidade": i.quantidade}
                        for i in self._itens
                    ],
                    "valor_total": self.valor_total,
                },
            )
            self.event_bus.publicar(evento)

    # -------------------------------------------------------------------------
    # Representação
    # -------------------------------------------------------------------------

    def __str__(self) -> str:
        return (
            f"Pedido #{self.id[:8]} | Cliente: {self.cliente} | "
            f"Estado: {self._estado.nome} | "
            f"Itens: {len(self._itens)} | Total: R$ {self.valor_total:.2f}"
        )
