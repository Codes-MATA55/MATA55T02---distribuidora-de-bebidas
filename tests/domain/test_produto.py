import unittest
from domain.entities.produto import Product


class TestProduct(unittest.TestCase):
    def setUp(self):
        self.valid_product = Product(
            id= '2',
            brand="Ambev",
            name="Cerveja Antarctica",
            description="Lata 350ml",
            barcode="7891000100011",
            price=4.50,
            amount_stock=100,
            supplier="Distribuidora Central"
        )

    def test_create_product_success(self):
        self.assertEqual(self.valid_product.name, "Cerveja Antarctica")
        self.assertEqual(self.valid_product.amount_stock, 100)

    def test_negative_price(self):
        with self.assertRaises(ValueError):
            Product("Ambev", "Nome", "Desc", "123", -1.0, 10, "Fornecedor")

    def test_negative_initial_amount(self):
        with self.assertRaises(ValueError):
            Product("Ambev", "Nome", "Desc", "123", 4.50, -5, "Fornecedor")

    def test_add_stock(self):
        self.valid_product.add_stock(50)
        self.assertEqual(self.valid_product.amount_stock, 150)

    def test_error_invalid_amount(self):
        with self.assertRaises(ValueError):
            self.valid_product.add_stock(0)

    def test_remove_stock(self):
        self.valid_product.remove_stock(40)
        self.assertEqual(self.valid_product.amount_stock, 60)

    def test_error_remove_amount(self):
        with self.assertRaises(ValueError):
            self.valid_product.remove_stock(150)
