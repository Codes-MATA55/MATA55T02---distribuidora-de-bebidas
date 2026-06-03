from dataclasses import dataclass

@dataclass
class Produto:
    marca: str
    nome: str
    descricao: str
    codbarras: str
    preco: float
    qtestoque: int
    fornecedor: str

    def __post_init__(self):
        if self.preco < 0:
            raise ValueError("Preço não pode ser negativo")
        if self.qtestoque < 0:
            raise ValueError("Quantidade em estoque não pode ser negativa")

    def adicionar_estoque(self, quantidade: int):
        if quantidade <= 0:
            raise ValueError("A quantidade a adicionar deve ser maior que zero")
        self.qtestoque += quantidade

    def remover_estoque(self, quantidade: int):
        if quantidade <= 0:
            raise ValueError("A quantidade a remover deve ser maior que zero")
        if quantidade > self.qtestoque:
            raise ValueError("Saldo insuficiente em estoque")
        self.qtestoque -= quantidade