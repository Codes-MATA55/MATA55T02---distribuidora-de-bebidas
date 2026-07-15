from datetime import date, timedelta
from pathlib import Path

from domain.entities.registro_estoque import StockRegistry
from domain.entities.separacao_total import TotalSeparation
from domain.factories import BatchFactory, OrderFactory, ProductFactory
from domain.json_storage import read_json, write_json
from domain.notifications import MemoryShipmentNotifier
from domain.order_workflow import OrderWorkflow
from domain.policies import FefoBatchSelectionPolicy
from domain.repositories.json_order_repository import JsonOrderRepository

class User:
    def __init__(self, id, name, role):
        self.id = id
        self.name = name
        self.role = role


class Role:
    def __init__(self, id, name, position, salary):
        self.id = id
        self.name = name
        self.position = position
        self.salary = salary


class Brand:
    def __init__(self, id, name):
        self.id = id
        self.name = name


class Category:
    def __init__(self, id, name):
        self.id = id
        self.name = name

BASE_DIR = Path(__file__).resolve().parent
DUMMY_DATA_FILE = BASE_DIR / "dummy_data.json"
ORDERS_FILE = BASE_DIR / "orders.json"

def build_product(product_data: dict):
    return ProductFactory.from_dict(product_data)


def build_stock(product, batches_data: list[dict]) -> StockRegistry:
    stock = StockRegistry()
    for batch_data in batches_data:
        batch = BatchFactory.from_dict(batch_data, product)
        stock.receive_batch(batch, reason="Dummy data inbound batch")
    return stock


def run_demo(order_repository=None, shipment_notifier=None) -> dict:
    data = read_json(DUMMY_DATA_FILE, default={})
    product = build_product(data["products"][0])
    stock = build_stock(product, data["batches"])
    order = OrderFactory.from_dict(data["orders"][0], product)

    repository = order_repository or JsonOrderRepository(ORDERS_FILE)
    notifier = shipment_notifier or MemoryShipmentNotifier()
    separation_service = TotalSeparation(FefoBatchSelectionPolicy())
    workflow = OrderWorkflow(repository, separation_service, notifier)
    tracking_code = workflow.confirm_separate_ship(order, stock, reference_date=date.today())

    result = {
        "product": product.to_dict(),
        "order": order.to_dict(),
        "tracking_code": tracking_code,
        "stock": stock.to_dict(),
        "notifications": getattr(notifier, "messages", []),
    }
    return result

if __name__ == "__main__":
    if not DUMMY_DATA_FILE.exists():
        tomorrow = date.today() + timedelta(days=1)
        write_json(
            DUMMY_DATA_FILE,
            {
                "products": [
                    {
                        "id": "P-JUICE-001",
                        "brand": "Fresh",
                        "name": "Orange Juice 1L",
                        "description": "Whole orange juice bottle",
                        "barcode": "7891234567890",
                        "price": 6.5,
                        "supplier": "Fornecedor Mockado",
                        "category": "SUCO",
                    }
                ],
                "batches": [
                    {"initial_amount": 200, "expiration_date": tomorrow.isoformat()},
                ],
                "orders": [{"amount": 120, "unit_price": "6,50"}],
            },
        )

    demo = run_demo()
    print(
        f"Order {demo['order']['id']} shipped with tracking "
        f"{demo['tracking_code']} and status {demo['order']['status']}"
    )