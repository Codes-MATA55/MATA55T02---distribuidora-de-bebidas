from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass(frozen=True)
class Evento:
    """
    Representa um evento de domínio imutável.
    Cada evento carrega informações sobre o que ocorreu.
    """
    tipo: str
    dados: dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.now)

    def __str__(self) -> str:
        return f"Evento(tipo={self.tipo!r}, timestamp={self.timestamp:%H:%M:%S})"


class Observer(ABC):
    """
    Interface base para todos os observadores (Subscriber).
    Define o contrato que qualquer observador deve implementar.
    """

    @abstractmethod
    def notificar(self, evento: Evento) -> None:
        """Processa um evento recebido."""
        ...


class EventBus:
    """
    Barramento de eventos (Publisher).
    Desacopla produtores de eventos dos seus consumidores.
    Implementa o padrão Observer de forma centralizada.
    """

    def __init__(self) -> None:
        self._assinantes: dict[str, list[Observer]] = {}

    def assinar(self, tipo_evento: str, observer: Observer) -> None:
        """Registra um observador para um tipo de evento."""
        if tipo_evento not in self._assinantes:
            self._assinantes[tipo_evento] = []
        self._assinantes[tipo_evento].append(observer)

    def publicar(self, evento: Evento) -> None:
        """Publica um evento para todos os observadores registrados."""
        assinantes = self._assinantes.get(evento.tipo, [])
        for obs in assinantes:
            obs.notificar(evento)

    def assinar_todos(self, tipos: list[str], observer: Observer) -> None:
        """Registra um observador para múltiplos tipos de evento."""
        for tipo in tipos:
            self.assinar(tipo, observer)
