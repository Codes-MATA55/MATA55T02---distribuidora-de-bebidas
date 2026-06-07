import re
from dataclasses import dataclass


@dataclass(frozen=True)
class CNPJ:
    valor: str

    def __post_init__(self):
        cnpj = re.sub(r"\D", "", self.valor)
        if not self._valido(cnpj):
            raise ValueError("CNPJ invalido")
        object.__setattr__(self, "valor", cnpj)

    @staticmethod
    def _valido(cnpj: str) -> bool:
        if cnpj == cnpj[0] * 14:
            return False

        if len(cnpj) != 14:
            return False

        soma1 = 0
        for i in range(12):
            match i:
                case 0 | 8:
                    soma1 += int(cnpj[i]) * 5
                case 1 | 9:
                    soma1 += int(cnpj[i]) * 4
                case 2 | 10:
                    soma1 += int(cnpj[i]) * 3
                case 3 | 11:
                    soma1 += int(cnpj[i]) * 2
                case 4:
                    soma1 += int(cnpj[i]) * 9
                case 5:
                    soma1 += int(cnpj[i]) * 8
                case 6:
                    soma1 += int(cnpj[i]) * 7
                case 7:
                    soma1 += int(cnpj[i]) * 6

        resto1 = soma1 % 11

        verificador_1 = 0 if resto1 == 0 or resto1 == 1 else 11 - resto1

        if int(cnpj[12]) != verificador_1:
            return False

        soma2 = 0

        for i in range(13):
            match i:
                case 0 | 8:
                    soma2 += int(cnpj[i]) * 6
                case 1 | 9:
                    soma2 += int(cnpj[i]) * 5
                case 2 | 10:
                    soma2 += int(cnpj[i]) * 4
                case 3 | 11:
                    soma2 += int(cnpj[i]) * 3
                case 4 | 12:
                    soma2 += int(cnpj[i]) * 2
                case 5:
                    soma2 += int(cnpj[i]) * 9
                case 6:
                    soma2 += int(cnpj[i]) * 8
                case 7:
                    soma2 += int(cnpj[i]) * 7

        resto2 = soma2 % 11

        verificador_2 = 0 if resto2 == 0 or resto2 == 1 else 11 - resto2

        if int(cnpj[13]) != verificador_2:
            return False

        return True