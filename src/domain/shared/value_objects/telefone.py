import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Telefone:
    valor: str

    def __post_init__(self):
        telefone = re.sub(r"\D", "", self.valor)

        if len(telefone) not in (10, 11):
            raise ValueError("Telefone inválido")

        ddd = telefone[:2]
        numero = telefone[2:]

        if ddd.startswith("0"):
            raise ValueError("DDD inválido")

        if len(numero) == 9 and not numero.startswith("9"):
            raise ValueError("Celular inválido")

        if len(numero) == 8 and numero[0] not in "2345":
            raise ValueError("Telefone fixo inválido")

        object.__setattr__(self, "valor", telefone)