from __future__ import annotations
from abc import ABC, abstractmethod


class CarrierPort(ABC):
    @abstractmethod
    def dispatch(self, order_id: str) -> str:
        """Solicita o despacho do pedido na expedição e retorna o código de rastreio.

        A aplicação depende deste contrato, não da API da transportadora. A
        implementação concreta traduz a chamada para o sistema externo, mantendo
        o domínio isolado de detalhes de integração.
        """
