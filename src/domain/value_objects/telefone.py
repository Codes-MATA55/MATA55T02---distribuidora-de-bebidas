import re
from dataclasses import dataclass


@dataclass(frozen=True)
class Telefone:
    value: str

    def __post_init__(self):
        phone_number = re.sub(r"\D", "", self.value)

        if len(phone_number) not in (10, 11):
            raise ValueError("Telefone inválido")

        ddd = phone_number[:2]
        number = phone_number[2:]

        if ddd.startswith("0"):
            raise ValueError("DDD inválido")

        if len(number) == 9 and not number.startswith("9"):
            raise ValueError("Celular inválido")

        if len(number) == 8 and number[0] not in "2345":
            raise ValueError("Telefone fixo inválido")

        object.__setattr__(self, "value", phone_number)
