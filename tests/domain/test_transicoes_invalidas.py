import unittest
from datetime import date, timedelta

from domain.entities.lote import Batch
from domain.entities.pedido import Order
from domain.entities.produto import Product
from domain.entities.registro_estoque import StockRegistry
from domain.entities.separacao_total import TotalSeparation
from domain.enums.tipo_movimentacao import BeverageCategory
from domain.value_objects.item_pedido import OrderItem


class TestInvalidOrderTransitions(unittest.TestCase):
    def _product(self) -> Product:
        return Product(
            "P-JUICE-900",
            "Fresh",
            "Apple Juice 1L",
            "Whole apple juice",
            "7899999999999",
            6.5,
            0,
            "Fornecedor Mockado",
            BeverageCategory.JUICE,
        )

    def _order(self) -> Order:
        product = self._product()
        return Order([OrderItem(product.id, 5, "6,50")])

    def test_cannot_ship_order_before_separation(self):
        order = self._order()
        order.confirm_payment()

        with self.assertRaisesRegex(ValueError, "após separação total"):
            order.ship()

    def test_cannot_ship_order_twice(self):
        product = self._product()
        stock = StockRegistry()
        stock.receive_batch(Batch(product, 10, date.today() + timedelta(days=10)))
        order = Order([OrderItem(product.id, 5, "6,50")])
        order.confirm_payment()

        TotalSeparation().execute(order, stock_registry=stock)
        order.ship()

        with self.assertRaisesRegex(ValueError, "já foi expedido"):
            order.ship()

    def test_cannot_mark_order_as_separated_with_pending_items(self):
        order = self._order()
        order.confirm_payment()

        with self.assertRaisesRegex(ValueError, "itens pendentes"):
            order.mark_as_separated()

    def test_cannot_jump_from_waiting_payment_to_separated(self):
        order = self._order()

        with self.assertRaisesRegex(ValueError, "Não é permitido mudar"):
            order.update_status("SEPARADO")

    def test_cannot_finish_order_before_transport(self):
        order = self._order()

        with self.assertRaisesRegex(ValueError, "Não é permitido mudar"):
            order.end_order()

    def test_cannot_cancel_finished_order(self):
        product = self._product()
        stock = StockRegistry()
        stock.receive_batch(Batch(product, 10, date.today() + timedelta(days=10)))
        order = Order([OrderItem(product.id, 5, "6,50")])
        order.confirm_payment()
        TotalSeparation().execute(order, stock_registry=stock)
        order.ship()
        order.end_order()

        with self.assertRaisesRegex(ValueError, "Não é permitido mudar"):
            order.cancel_order()


if __name__ == "__main__":
    unittest.main()
