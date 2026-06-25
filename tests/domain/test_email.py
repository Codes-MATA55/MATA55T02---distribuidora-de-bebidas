import unittest
from domain.value_objects.email import Email


class TestEmail(unittest.TestCase):
    def test_valid_email(self):
        email = Email("compras@distribuidora.com.br")
        self.assertEqual(email.value, "compras@distribuidora.com.br")

    def test_email_spaces_and_lowercases(self):
        email = Email("  COMPRAS@distribuidora.com.br  ")
        self.assertEqual(email.value, "compras@distribuidora.com.br")

    def test_email_at_sign(self):
        with self.assertRaisesRegex(ValueError, "E-mail inválido"):
            Email("compras_distribuidora.com.br")

    def test_email_no_domain(self):
        with self.assertRaisesRegex(ValueError, "E-mail inválido"):
            Email("compras@")


if __name__ == '__main__':
    unittest.main()
