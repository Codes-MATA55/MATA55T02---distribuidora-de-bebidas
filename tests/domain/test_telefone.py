import unittest
from src.domain.shared.value_objects.telefone import Telefone


class TestTelefone(unittest.TestCase):
    def test_celular_valido(self):
        telefone = Telefone("71988887777")
        self.assertEqual(telefone.valor, "71988887777")

    def test_telefone_fixo_valido(self):
        telefone = Telefone("7133334444")
        self.assertEqual(telefone.valor, "7133334444")

    def test_ddd_iniciando_com_zero(self):
        with self.assertRaisesRegex(ValueError, "DDD inválido"):
            Telefone("01988887777")

    def test_celular_comeca_com_nove(self):
        with self.assertRaisesRegex(ValueError, "Celular inválido"):
            Telefone("71888887777")

    def test_telefone_fixo_iniciando_com_digito_invalido(self):
        with self.assertRaisesRegex(ValueError, "Telefone fixo inválido"):
            Telefone("7113334444")

    def test_limpar_mascaras(self):
        telefone = Telefone("(71) 98888-7777")
        self.assertEqual(telefone.valor, "71988887777")


if __name__ == '__main__':
    unittest.main()
