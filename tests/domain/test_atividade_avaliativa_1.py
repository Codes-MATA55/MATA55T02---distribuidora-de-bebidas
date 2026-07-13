import unittest
from datetime import date, timedelta

from src.domain.entities.lote import Batch
from src.domain.entities.produto import Product
from src.domain.enums.tipo_movimentacao import BeverageCategory
from src.domain.factories import BatchFactory, OrderFactory, ProductFactory
from src.domain.repositories.in_memory_order_repository import InMemoryOrderRepository
from src.domain.value_objects.item_pedido import OrderItem
from src.domain.value_objects.quantidade import Quantity


class TestTacticalDdd(unittest.TestCase):
    def _product(self) -> Product:
        return Product(
            "P-BEER-001",
            "Brewery",
            "Lager Beer 350ml",
            "Light lager beer can",
            "7891111111111",
            4.5,
            0,
            "Fornecedor Mockado",
            BeverageCategory.BEER,
        )

    def test_quantity_value_object_protects_negative_amount(self):
        with self.assertRaisesRegex(ValueError, "Quantity cannot be negative"):
            Quantity(-1)

        self.assertEqual(Quantity.positive(5).subtract(Quantity(2)).value, 3)

    def test_batch_uses_value_objects_without_changing_public_behavior(self):
        product = self._product()
        batch = Batch(product, 10, date.today() + timedelta(days=5))

        batch.consume_amount(4)

        self.assertEqual(batch.current_amount, 6)
        self.assertFalse(batch.is_expired())

    def test_order_aggregate_blocks_item_change_after_payment(self):
        product = self._product()
        order = OrderFactory.empty()
        order.add_item(OrderItem(product.id, 2, "4,50"))
        order.confirm_payment()

        with self.assertRaisesRegex(ValueError, "before payment confirmation"):
            order.add_item(OrderItem(product.id, 1, "4,50"))

    def test_factories_build_valid_domain_objects_from_json_like_data(self):
        product = ProductFactory.from_dict({
            "id": "P-SODA-001",
            "brand": "Fizz",
            "name": "Cola 2L",
            "description": "Cola bottle",
            "barcode": "7892222222222",
            "price": 8.0,
            "supplier": "Fornecedor Mockado",
            "category": "REFRIGERANTE",
        })
        batch = BatchFactory.from_dict(
            {"initial_amount": 30, "expiration_date": (date.today() + timedelta(days=10)).isoformat()},
            product,
        )
        order = OrderFactory.from_dict({"amount": 3, "unit_price": "8,00"}, product)

        self.assertEqual(product.category, BeverageCategory.SODA)
        self.assertEqual(batch.product.id, product.id)
        self.assertEqual(order.items[0].product_id, product.id)

    def test_in_memory_repository_saves_order_snapshot(self):
        product = self._product()
        order = OrderFactory.from_dict({"amount": 2, "unit_price": "4,50"}, product)
        repository = InMemoryOrderRepository()

        repository.save(order)

        self.assertEqual(repository.find_by_id(str(order.id))["id"], str(order.id))
        self.assertEqual(len(repository.list_all()), 1)


if __name__ == "__main__":
    unittest.main()
