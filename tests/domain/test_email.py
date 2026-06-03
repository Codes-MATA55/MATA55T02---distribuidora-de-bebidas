import unittest
from src.domain.shared.value_objects.email import Email


class TestEmail(unittest.TestCase):
    def test_email_valido(self):
        email = Email("compras@distribuidora.com.br")
        self.assertEqual(email.valor, "compras@distribuidora.com.br")

    def test_email_espacos_e_lowercase(self):
        email = Email("  COMPRAS@distribuidora.com.br  ")
        self.assertEqual(email.valor, "compras@distribuidora.com.br")

    def test_email_arroba(self):
        with self.assertRaisesRegex(ValueError, "E-mail inválido"):
            Email("compras_distribuidora.com.br")

    def test_email_sem_dominio(self):
        with self.assertRaisesRegex(ValueError, "E-mail inválido"):
            Email("compras@")


if __name__ == '__main__':
    unittest.main()
