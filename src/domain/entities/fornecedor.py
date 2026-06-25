from domain.value_objects.cnpj import CNPJ
from domain.value_objects.email import Email
from domain.value_objects.telefone import PhoneNumber
from domain.value_objects.ids import FornecedorId


class Fornecedor:
    def __init__(self, name: str, cnpj: CNPJ, phone_number: PhoneNumber, email: Email, id: FornecedorId = None):
        self.id = id or FornecedorId()
        self.name = name
        self.cnpj = cnpj
        self.phone_number = phone_number
        self.email = email
