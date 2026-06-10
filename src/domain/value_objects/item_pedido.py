from dataclasses import dataclass, field
from .dinheiro import Dinheiro


@dataclass(frozen=True)
class ItemPedido:
    id_produto: int
    quantidade: int
    preco_unitario_str: str
    preco_unitario: Dinheiro = field(init=False)

    def __post_init__(self):
        if not isinstance(self.id_produto, int):
            raise ValueError("ID do produto inválido")

        if not isinstance(self.quantidade, int) or self.quantidade <= 0:
            raise ValueError("Quantidade inválida")
        
        object.__setattr__(self, "preco_unitario", Dinheiro(self.preco_unitario_str))        
    
    def calcular_subtotal(self) -> Dinheiro:
        quantia_centavos = self.preco_unitario.valor * self.quantidade
        quantia_string = Dinheiro.converter_centavos_para_string(quantia_centavos)

        return Dinheiro(quantia_string)