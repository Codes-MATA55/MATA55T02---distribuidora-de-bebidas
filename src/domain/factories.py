from datetime import date

from domain.entities.lote import Batch
from domain.entities.pedido import Order
from domain.entities.produto import Product
from domain.enums.tipo_movimentacao import BeverageCategory
from domain.value_objects.item_pedido import OrderItem


class ProductFactory:
    @staticmethod
    def from_dict(product_data: dict) -> Product:
        return Product(
            id=product_data["id"],
            brand=product_data["brand"],
            name=product_data["name"],
            description=product_data["description"],
            barcode=product_data["barcode"],
            price=product_data["price"],
            amount_stock=product_data.get("amount_stock", 0),
            supplier=product_data["supplier"],
            category=BeverageCategory(product_data["category"]),
        )


class BatchFactory:
    @staticmethod
    def from_dict(batch_data: dict, product: Product) -> Batch:
        return Batch(
            product=product,
            initial_amount=batch_data["initial_amount"],
            expiration_date=date.fromisoformat(batch_data["expiration_date"]),
        )


class OrderFactory:
    @staticmethod
    def empty() -> Order:
        return Order(items=[])

    @staticmethod
    def from_dict(order_data: dict, product: Product) -> Order:
        order = OrderFactory.empty()
        order.add_item(OrderItem(product.id, order_data["amount"], order_data["unit_price"]))
        return order
