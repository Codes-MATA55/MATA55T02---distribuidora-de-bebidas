import re
from dataclasses import dataclass


@dataclass(frozen=True)
class CPF:
    value: str

    def __post_init__(self):
        pattern = re.compile(r"^(?:\d{11}|\d{3}\.\d{3}\.\d{3}-\d{2})$")
        if not pattern.fullmatch(self.value):
            raise ValueError("Formato de CPF inválido")
        cpf = re.sub(r"\D", "", self.value)

        if not self._valid(cpf):
            raise ValueError("Número de CPF inválido")

        object.__setattr__(self, "value", cpf)

    @staticmethod
    def _valid(cpf: str) -> bool:
        if len(cpf) != 11:
            return False

        if cpf == cpf[0] * 11:
            return False

        sum1 = sum(int(cpf[i]) * (10 - i) for i in range(9))
        digit1 = (sum1 * 10) % 11
        digit1 = 0 if digit1 == 10 else digit1

        sum2 = sum(int(cpf[i]) * (11 - i) for i in range(10))
        digit2 = (sum2 * 10) % 11
        digit2 = 0 if digit2 == 10 else digit2

        return digit1 == int(cpf[9]) and digit2 == int(cpf[10])
