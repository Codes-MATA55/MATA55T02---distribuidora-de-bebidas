import re
from dataclasses import dataclass, field


@dataclass(frozen=True)
class Dinheiro:
    valor: int = field(init=False)
    valor_str: str    

    def __post_init__(self):
        dinheiro_str = self.valor_str

        if not self._valido(dinheiro_str):
            raise ValueError("Valor ou formato inválido")
        
        dinheiro_int = int(re.sub(r"[.,]", "", dinheiro_str))

        object.__setattr__(self, "valor_str", dinheiro_str)
        object.__setattr__(self, "valor", dinheiro_int)

    @staticmethod
    def _valido(dinheiro_str: str) -> bool:    
        
        padrao = re.compile(r"^(?:\d{1,3}(?:\.\d{3})*),\d{2}$")
        if not padrao.fullmatch(dinheiro_str):
            return False
        
        dinheiro_int = int(re.sub(r"[.,]", "", dinheiro_str))
        if dinheiro_int < 0:
            return False
        return True

        