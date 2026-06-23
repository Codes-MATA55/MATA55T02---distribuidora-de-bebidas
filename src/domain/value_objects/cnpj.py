import re
from dataclasses import dataclass


@dataclass(frozen=True)
class CNPJ:
    value: str

    def __post_init__(self):
        pattern = re.compile(r"\d{14}|\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}")        
        if not pattern.fullmatch(self.value):
            raise ValueError("Formato de CNPJ inválido")        
        
        cnpj = re.sub(r"\D", "", self.value)

        if not self._valid(cnpj):
            raise ValueError("Número de CNPJ inválido")

        object.__setattr__(self, "value", cnpj)

    @staticmethod
    def _valid(cnpj: str) -> bool:
        if len(cnpj) != 14:
            return False

        if cnpj == cnpj[0] * 14:
            return False   
                
        
        sum1 = 0
        for i in range(12):
            match i:
                case 0 | 8:
                    sum1 += int(cnpj[i]) * 5
                case 1 | 9:
                    sum1 += int(cnpj[i]) * 4
                case 2 | 10:
                    sum1 += int(cnpj[i]) * 3  
                case 3 | 11:
                    sum1 += int(cnpj[i]) * 2 
                case 4:
                    sum1 += int(cnpj[i]) * 9 
                case 5:
                    sum1 += int(cnpj[i]) * 8
                case 6:
                    sum1 += int(cnpj[i]) * 7
                case 7:
                    sum1 += int(cnpj[i]) * 6   
        
        remainder1 = sum1 % 11
        
        check1 = 0 if remainder1 == 0 or remainder1 == 1 else 11 - remainder1
        
        if int(cnpj[12]) != check1:
            return False
        
        sum2 = 0
        
        for i in range(13):
            match i:
                case 0 | 8:
                    sum2 += int(cnpj[i]) * 6
                case 1 | 9:
                    sum2 += int(cnpj[i]) * 5
                case 2 | 10:
                    sum2 += int(cnpj[i]) * 4  
                case 3 | 11:
                    sum2 += int(cnpj[i]) * 3 
                case 4 | 12:
                    sum2 += int(cnpj[i]) * 2 
                case 5:
                    sum2 += int(cnpj[i]) * 9
                case 6:
                    sum2 += int(cnpj[i]) * 8
                case 7:
                    sum2 += int(cnpj[i]) * 7
                
        remainder2 = sum2 % 11
        
        check2 = 0 if remainder2 == 0 or remainder2 == 1 else 11 - remainder2
        
        if int(cnpj[13]) != check2:
            return False
        
        return True
