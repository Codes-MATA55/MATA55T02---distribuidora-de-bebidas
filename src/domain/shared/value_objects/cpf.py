import re
from dataclasses import dataclass


@dataclass(frozen=True)
class CPF:
    valor: str

    def __post_init__(self):
        cpf = re.sub(r"\D", "", self.valor)

        if not self._valido(cpf):
            raise ValueError("CPF inválido")

        object.__setattr__(self, "valor", cpf)

    @staticmethod
    def _valido(cpf: str) -> bool:
        if len(cpf) != 11:
            return False

        if cpf == cpf[0] * 11:
            return False

        soma = sum(int(cpf[i]) * (10 - i) for i in range(9))
        digito1 = (soma * 10) % 11
        digito1 = 0 if digito1 == 10 else digito1

        soma = sum(int(cpf[i]) * (11 - i) for i in range(10))
        digito2 = (soma * 10) % 11
        digito2 = 0 if digito2 == 10 else digito2

        return digito1 == int(cpf[9]) and digito2 == int(cpf[10])
