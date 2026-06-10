from domain.value_objects.cnpj import CNPJ
from domain.value_objects.email import Email
from domain.value_objects.telefone import Telefone
from domain.value_objects.ids import FornecedorId


class Fornecedor:
    def __init__(self, nome: str, cnpj: CNPJ, telefone: Telefone, email: Email, id: FornecedorId = None):
        self.id = id or FornecedorId()
        self.nome = nome
        self.cnpj = cnpj
        self.telefone = telefone
        self.email = email
