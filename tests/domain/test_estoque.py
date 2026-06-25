import unittest
from domain.entities.produto import Product
from domain.enums.tipo_movimentacao import MovementType
from domain.entities.movimentacao_estoque import StockMovement


class TestStock(unittest.TestCase):
    def setUp(self):
        self.product = Product(
            id='1',
            brand="Coca-Cola",
            name="Refri Coca",
            description="Pet 2L",
            barcode="7892000200022",
            price=8.00,
            amount_stock=50,
            supplier="Coca-Cola BR"
        )

    def test_stock_inbound_succeeds(self):
        movimentacao = StockMovement(
            id=1,
            product=self.product,
            type=MovementType.INBOUND,
            amount=20
        )
        self.assertEqual(self.product.amount_stock, 70)
        self.assertEqual(movimentacao.amount, 20)

    def test_stock_oubound_succeeds(self):
        movimentacao = StockMovement(
            id=2,
            product=self.product,
            type=MovementType.OUTBOUND,
            amount=10
        )
        self.assertEqual(self.product.amount_stock, 40)

    def test_stock_outbound_when_stock_is_insufficient(self):
        with self.assertRaises(ValueError):
            StockMovement(
                id=3,
                product=self.product,
                type=MovementType.OUTBOUND,
                amount=60
            )

    def test_inbound_for_invalid_quantity(self):
        with self.assertRaises(ValueError):
            StockMovement(
                id=4,
                product=self.product,
                type=MovementType.INBOUND,
                amount=0
            )
