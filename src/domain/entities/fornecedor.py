from domain.value_objects.cnpj import CNPJ
from domain.value_objects.email import Email
from domain.value_objects.telefone import Telefone


class Fornecedor:
    def __init__(self, id: int, nome: str, cnpj: CNPJ, telefone: Telefone, email: Email):
        self.id = id
        self.nome = nome
        self.cnpj = cnpj
        self.telefone = telefone
        self.email = email
