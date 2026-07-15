from typing import List
from datetime import date

from domain.entities.lote import Batch
from domain.entities.pedido import Order
from domain.entities.registro_estoque import StockRegistry

class TotalSeparation:

    def execute(
        self,
        order: Order,
        available_batches: List[Batch] | None = None,
        reference_date: date = None,
        stock_registry: StockRegistry | None = None,
    ) -> None:
        if reference_date is None:
            reference_date = date.today()

        if order.status != "EM PROCESSAMENTO":
            raise ValueError(
                f"Não é possível separar o pedido {order.id}. "
                f"Status atual inválido: {order.status}"
            )

        if stock_registry is not None:
            self._execute_with_stock_registry(order, stock_registry, reference_date)
            return

        batches = available_batches or []
        self._validate_available_batches(order, batches, reference_date)
        self._consume_available_batches(order, batches, reference_date)
        order.mark_as_separated()

    def _validate_available_batches(
        self,
        order: Order,
        available_batches: List[Batch],
        reference_date: date,
    ) -> None:
        for item in order.items:
            order_item_id = getattr(item, "product_id", None)
            necessary_amount = getattr(item, "amount", 0)

            if not order_item_id:
                raise ValueError("Item de pedido não possui um produto associado.")

            product_batches = [
                batch
                for batch in available_batches
                if str(batch.product.id) == str(order_item_id)
                and not batch.is_expired(reference_date)
            ]

            total_available = sum(batch.current_amount for batch in product_batches)

            if total_available < necessary_amount:
                raise ValueError(
                    f"Separação inválida para o produto '{order_item_id}'. "
                    f"Necessário: {necessary_amount}, disponível em lotes válidos: {total_available}"
                )

    def _consume_available_batches(
        self,
        order: Order,
        available_batches: List[Batch],
        reference_date: date,
    ) -> None:
        for item in order.items:
            order_item_id = getattr(item, "product_id", None)
            remaining_amount = getattr(item, "amount", 0)

            product_batches = self._batch_selection_policy.order_batches([
                batch
                for batch in available_batches
                if str(batch.product.id) == str(order_item_id)
                and not batch.is_expired(reference_date)
            ])

            for batch in product_batches:
                if remaining_amount <= 0:
                    break

                amount_to_remove = min(batch.current_amount, remaining_amount)
                batch.consume_amount(amount_to_remove)
                item.mark_separated(amount_to_remove)
                remaining_amount -= amount_to_remove

    def _execute_with_stock_registry(
        self,
        order: Order,
        stock_registry: StockRegistry,
        reference_date: date,
    ) -> None:
        for item in order.items:
            stock_registry.withdraw(
                item.product_id,
                item.amount,
                reference_date=reference_date,
                reason=f"Order separation {order.id}",
                batch_selection_policy=self._batch_selection_policy,
            )
            item.mark_separated(item.amount)

        order.mark_as_separated()
