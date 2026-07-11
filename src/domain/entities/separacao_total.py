from typing import List
from datetime import date

class TotalSeparation:

    def execute(self, order: 'Order', available_batches: List['Batch'], reference_date: date = None) -> None:
        reference_date = reference_date or date.today()

        self._validate_order_status(order)
        self._validate_stock_availability(order, available_batches, reference_date)
        self._process_separation(order, available_batches, reference_date)

        order.update_status("SEPARADO")

    def _validate_order_status(self, order: 'Order') -> None:
        if order.status != "EM PROCESSAMENTO":
            raise ValueError(
                f"Não é possível separar o pedido {order.id}. "
                f"Status atual inválido: {order.status}"
            )

    def _get_valid_batches(self, product_id: int, available_batches: List['Batch'], reference_date: date) -> List['Batch']:
        
        return [
            batch for batch in available_batches
            if batch._product._id == product_id and not batch.is_expired(reference_date)
        ]

    def _validate_stock_availability(self, order: 'Order', available_batches: List['Batch'], reference_date: date) -> None:
        
        for item in order.items:
            product_id = getattr(item, "product_id", None)
            necessary_amount = getattr(item, "amount", 0)

            if not product_id:
                raise ValueError("Item de pedido não possui um produto associado.")

            product_batches = self._get_valid_batches(product_id, available_batches, reference_date)
            total_available = sum(batch._current_amount for batch in product_batches)

            if total_available < necessary_amount:
                raise ValueError(
                    f"Separação inválida para o produto '{product_id}'. "
                    f"Necessário: {necessary_amount}, disponível em lotes válidos: {total_available}"
                )

    def _process_separation(self, order: 'Order', available_batches: List['Batch'], reference_date: date) -> None:
        for item in order.items:
            product_id = getattr(item, "product_id", None)
            remaining_amount = getattr(item, "amount", 0)

            valid_batches = self._get_valid_batches(product_id, available_batches, reference_date)

            # Ordena os lotes pela data de validade (FIFO)

            sorted_batches = sorted(valid_batches, key=lambda batch: batch.expiration_date)

            self._consume_batches(sorted_batches, remaining_amount)
            
            # REVER BAIXA DE ESTOQUE
            # product.decrease_stock(getattr(item, "amount", 0))

    def _consume_batches(self, sorted_batches: List['Batch'], remaining_amount: int) -> None:
   
        for batch in sorted_batches:
            if remaining_amount <= 0:
                break

            amount_to_remove = min(batch._current_amount, remaining_amount)
            batch.consume_amount(amount_to_remove)
            remaining_amount -= amount_to_remove