class Usuario:
    def __init__(self, id, nome, cargo):
        self.id = id
        self.nome = nome
        self.cargo = cargo


class Cargo:
    def __init__(self, id, nome, funcao, salario):
        self.id = id
        self.nome = nome
        self.funcao = funcao
        self.salario = salario


class Marca:
    def __init__(self, id, nome):
        self.id = id
        self.nome = nome


class Categoria:
    def __init__(self, id, nome):
        self.id = id
        self.nome = nome
