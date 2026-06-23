import re
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Dinheiro:
    value: int = field(init=False)
    value_str: str    

    def __post_init__(self):
        if not isinstance(self.value_str, str):
            raise ValueError("value não está no formato string")      
          
        dinheiro_str = self.value_str

        if not self._valid(dinheiro_str):
            raise ValueError("value ou formato inválido")
        
        dinheiro_int = int(re.sub(r"[.,]", "", dinheiro_str))

        object.__setattr__(self, "value_str", dinheiro_str)
        object.__setattr__(self, "value", dinheiro_int)

    @staticmethod
    def _valid(dinheiro_str: str) -> bool:    
        
        pattern = re.compile(r"^(?:\d{1,3}(?:\.\d{3})*),\d{2}$")
        if not pattern.fullmatch(dinheiro_str):
            return False
        
        dinheiro_int = int(re.sub(r"[.,]", "", dinheiro_str))
        if dinheiro_int < 0:
            return False
        return True
    
    @staticmethod
    def convert_cents_to_string( cents: int) -> str:
        reais = cents // 100
        remaining_cents = cents % 100

        value_str = (f"{reais:,}".replace(",", ".") + f",{remaining_cents:02d}")

        return value_str   

        