from datetime import date
from typing import List

from domain.entities.lote import Batch
from domain.entities.pedido import Order
from domain.entities.produto import Product
from domain.value_objects.item_pedido import OrderItem


class TotalSeparation:
    """Serviço de domínio para separação total com estratégia FEFO."""

    def execute(self, order: Order, available_batches: List[Batch], reference_date: date = None) -> None:
        if reference_date is None:
            reference_date = date.today()

        if order.status != "EM PROCESSAMENTO":
            raise ValueError(
                f"Não é possível separar o pedido {order.id}. "
                f"Status atual inválido: {order.status}"
            )

        for item in order.items:
            order_item_id = getattr(item, "product_id", None)
            necessary_amount = getattr(item, "amount", 0)

            if not order_item_id:
                raise ValueError("Item de pedido não possui um produto associado.")

            product_batches = [
                batch for batch in available_batches
                if batch._product._id == order_item_id
                and not batch.is_expired(reference_date)
            ]

            total_available = sum(batch._current_amount for batch in product_batches)

            if total_available < necessary_amount:
                raise ValueError(
                    f"Separação inválida para o produto '{product._name}'. "
                    f"Necessário: {necessary_amount}, disponível em lotes válidos: {total_available}"
                )

        for item in order.items:
            order_item_id = getattr(item, "product_id", None)
            remaining_amount = getattr(item, "amount", 0)

            product_batches = sorted(
                [
                    batch for batch in available_batches
                    if batch._product._id == order_item_id
                    and not batch.is_expired(reference_date)
                ],
                key=lambda batch: batch.expiration_date,
            )

            for batch in product_batches:
                if remaining_amount <= 0:
                    break

                amount_to_remove = min(batch._current_amount, remaining_amount)
                batch.consume_amount(amount_to_remove)
                remaining_amount -= amount_to_remove

            product.decrease_stock(getattr(item, "amount", 0))

        order.update_status("SEPARADO")
