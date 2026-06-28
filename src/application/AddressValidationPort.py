from __future__ import annotations
from abc import ABC, abstractmethod


class AddressValidationPort(ABC):
    @abstractmethod
    def resolve(self, zip_code: str) -> str:
        """Valida e resolve um CEP no endereço correspondente.

        Abstrai um serviço externo de CEP. A implementação concreta encapsula o
        formato do serviço, expondo apenas o endereço já resolvido.
        """
