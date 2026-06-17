class Produto:
    def __init__(
        self,
        marca: str,
        nome: str,
        descricao: str,
        codigo_barras: str,
        preco: float,
        quantidade_estoque: int,
        fornecedor: str
    ):
        if not marca or not marca.strip():
            raise ValueError("Marca é obrigatória")

        if not nome or not nome.strip():
            raise ValueError("Nome é obrigatório")

        if preco < 0:
            raise ValueError("Preço não pode ser negativo")

        if quantidade_estoque < 0:
            raise ValueError("Quantidade em estoque não pode ser negativa")

        self._marca = marca.strip()
        self._nome = nome.strip()
        self._descricao = descricao.strip()
        self._codigo_barras = codigo_barras.strip()
        self._preco = preco
        self._quantidade_estoque = quantidade_estoque
        self._fornecedor = fornecedor

    @property
    def marca(self):
        return self._marca

    @property
    def nome(self):
        return self._nome

    @property
    def descricao(self):
        return self._descricao

    @property
    def codigo_barras(self):
        return self._codigo_barras

    @property
    def codbarras(self):
        return self.codigo_barras

    @property
    def preco(self):
        return self._preco

    @property
    def quantidade_estoque(self):
        return self._quantidade_estoque

    @property
    def qtestoque(self):
        return self.quantidade_estoque

    @property
    def fornecedor(self):
        return self._fornecedor

    def adicionar_estoque(self, quantidade: int):
        if quantidade <= 0:
            raise ValueError("A quantidade a adicionar deve ser maior que zero")

        self._quantidade_estoque += quantidade

    def baixar_estoque(self, quantidade: int):
        if quantidade <= 0:
            raise ValueError("A quantidade a remover deve ser maior que zero")

        if quantidade > self._quantidade_estoque:
            raise ValueError("Saldo insuficiente em estoque")

        self._quantidade_estoque -= quantidade

    def remover_estoque(self, quantidade: int):
        self.baixar_estoque(quantidade)

    def alterar_preco(self, novo_preco: float):
        if novo_preco < 0:
            raise ValueError("Preço não pode ser negativo")

        self._preco = novo_preco

    def alterar_descricao(self, nova_descricao: str):
        if not nova_descricao or not nova_descricao.strip():
            raise ValueError("Descrição não pode ser vazia")

        self._descricao = nova_descricao.strip()
