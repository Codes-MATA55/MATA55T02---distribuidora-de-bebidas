import unittest
from src.domain.shared.value_objects.cpf import CPF


class TestCPF(unittest.TestCase):
    def test_cpf_valido(self):
        cpf = CPF("11144477735")
        self.assertEqual(cpf.valor, "11144477735")

    def test_cpf_tamanho_invalido(self):
        with self.assertRaisesRegex(ValueError, "CPF inválido"):
            CPF("123")

    def test_cpf_numeros_iguais(self):
        with self.assertRaisesRegex(ValueError, "CPF inválido"):
            CPF("11111111111")

    def test_cpf_caracteres_nao_numericos(self):
        cpf = CPF("111.444.777-35")
        self.assertEqual(cpf.valor, "11144477735")
        
    def test_cpf_digitos_verificadores_errados(self):
        with self.assertRaisesRegex(ValueError, "CPF inválido"):
            CPF("11144477736")


if __name__ == '__main__':
    unittest.main()
