import tempfile
import unittest
from datetime import date, timedelta
from pathlib import Path

from src.domain.entities.lote import Batch
from src.domain.entities.pedido import Order
from src.domain.entities.produto import Product
from src.domain.entities.registro_estoque import StockRegistry
from src.domain.entities.separacao_total import TotalSeparation
from src.domain.enums.tipo_movimentacao import BeverageCategory
from src.domain.notifications import MemoryShipmentNotifier
from src.domain.order_workflow import OrderWorkflow
from src.domain.policies import FefoBatchSelectionPolicy, LifoBatchSelectionPolicy
from src.domain.repositories.in_memory_order_repository import InMemoryOrderRepository
from src.domain.repositories.json_order_repository import JsonOrderRepository
from src.domain.value_objects.item_pedido import OrderItem


class TestDipAndDi(unittest.TestCase):
    def _product(self) -> Product:
        return Product(
            "P-JUICE-002",
            "Fresh",
            "Grape Juice 1L",
            "Whole grape juice",
            "7893333333333",
            7.0,
            0,
            "Fornecedor Mockado",
            BeverageCategory.JUICE,
        )

    def test_lifo_policy_changes_batch_consumption_without_changing_stock_registry(self):
        product = self._product()
        first_expiration = Batch(product, 100, date.today() + timedelta(days=5))
        last_expiration = Batch(product, 100, date.today() + timedelta(days=30))
        stock = StockRegistry()
        stock.receive_batch(first_expiration)
        stock.receive_batch(last_expiration)
        order = Order([OrderItem(product.id, 80, "7,00")])
        order.confirm_payment()

        TotalSeparation(LifoBatchSelectionPolicy()).execute(order, stock_registry=stock)

        self.assertEqual(first_expiration.current_amount, 100)
        self.assertEqual(last_expiration.current_amount, 20)
        self.assertEqual(order.status, "SEPARADO")

    def test_workflow_uses_injected_repository_policy_and_notifier(self):
        product = self._product()
        stock = StockRegistry()
        stock.receive_batch(Batch(product, 10, date.today() + timedelta(days=5)))
        order = Order([OrderItem(product.id, 4, "7,00")])
        repository = InMemoryOrderRepository()
        notifier = MemoryShipmentNotifier()
        workflow = OrderWorkflow(
            repository,
            TotalSeparation(FefoBatchSelectionPolicy()),
            notifier,
        )

        tracking_code = workflow.confirm_separate_ship(order, stock, reference_date=date.today())

        self.assertTrue(tracking_code.startswith("TRK-"))
        self.assertIsNotNone(repository.find_by_id(str(order.id)))
        self.assertEqual(len(notifier.messages), 1)

    def test_json_repository_persists_snapshot_behind_contract(self):
        product = self._product()
        order = Order([OrderItem(product.id, 1, "7,00")])

        with tempfile.TemporaryDirectory() as directory:
            repository = JsonOrderRepository(Path(directory) / "orders.json")
            repository.save(order)

            self.assertEqual(repository.find_by_id(str(order.id))["id"], str(order.id))
            self.assertEqual(len(repository.list_all()), 1)


if __name__ == "__main__":
    unittest.main()
