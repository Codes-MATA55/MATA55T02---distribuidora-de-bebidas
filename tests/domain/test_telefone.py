import unittest
from domain.value_objects.telefone import PhoneNumber


class TestPhoneNumber(unittest.TestCase):
    def test_valid_cellphone_number(self):
        telefone = PhoneNumber("71988887777")
        self.assertEqual(telefone.value, "71988887777")

    def test_valid_telephone_number(self):
        telefone = PhoneNumber("7133334444")
        self.assertEqual(telefone.value, "7133334444")

    def test__ddd_startswith_zero(self):
        with self.assertRaisesRegex(ValueError, "DDD inválido"):
            PhoneNumber("01988887777")

    def test_cellphone_startswith_nine(self):
        with self.assertRaisesRegex(ValueError, "Celular inválido"):
            PhoneNumber("71888887777")

    def test_telephone_startswith_invalid_digit(self):
        with self.assertRaisesRegex(ValueError, "Telefone fixo inválido"):
            PhoneNumber("7113334444")

    def test_lclean_masks(self):
        telefone = PhoneNumber("(71) 98888-7777")
        self.assertEqual(telefone.value, "71988887777")


if __name__ == '__main__':
    unittest.main()
