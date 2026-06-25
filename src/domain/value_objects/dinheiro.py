import re
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Money:
    value: int = field(init=False)
    value_str: str    

    def __post_init__(self):
        if not isinstance(self.value_str, str):
            raise ValueError("value não está no formato string")      
          
        money_str = self.value_str

        if not self._valid(money_str):
            raise ValueError("value ou formato inválido")
        
        money_int = int(re.sub(r"[.,]", "", money_str))

        object.__setattr__(self, "value_str", money_str)
        object.__setattr__(self, "value", money_int)

    @staticmethod
    def _valid(money_str: str) -> bool:    
        
        pattern = re.compile(r"^(?:\d{1,3}(?:\.\d{3})*),\d{2}$")
        if not pattern.fullmatch(money_str):
            return False
        
        money_int = int(re.sub(r"[.,]", "", money_str))
        if money_int < 0:
            return False
        return True
    
    @staticmethod
    def convert_cents_to_string( cents: int) -> str:
        reais = cents // 100
        remaining_cents = cents % 100

        value_str = (f"{reais:,}".replace(",", ".") + f",{remaining_cents:02d}")

        return value_str