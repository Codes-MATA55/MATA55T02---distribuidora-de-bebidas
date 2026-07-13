from datetime import date
from typing import List

from domain.entities.lote import Batch
from domain.entities.movimentacao_estoque import StockMovement
from domain.enums.tipo_movimentacao import MovementType
from domain.policies import BatchSelectionPolicy, FefoBatchSelectionPolicy


class StockRegistry:
    def __init__(self):
        self._movements: List[StockMovement] = []
        self._batches: List[Batch] = []

    def register(self, movement: StockMovement):
        self._movements.append(movement)

    def list_history(self) -> List[StockMovement]:
        return list(self._movements)
    
    def receive_batch(self, batch: Batch, reason: str = "Stock batch received") -> StockMovement:
        self._batches.append(batch)
        movement = StockMovement(
            batch.product,
            MovementType.INBOUND,
            batch.initial_amount,
            batch_id=batch.id,
            reason=reason,
        )
        self.register(movement)
        return movement

    def list_batches(self) -> List[Batch]:
        return list(self._batches)

    def valid_batches_for(self, product_id: str | int, reference_date: date = None) -> List[Batch]:
        if reference_date is None:
            reference_date = date.today()
        return [
            batch
            for batch in self._batches
            if str(batch.product.id) == str(product_id) and not batch.is_expired(reference_date)
        ]

    def balance_for_product(self, product_id: str | int, reference_date: date = None) -> int:
        return sum(batch.current_amount for batch in self.valid_batches_for(product_id, reference_date))

    def withdraw_fefo(
        self,
        product_id: str | int,
        amount: int,
        reference_date: date = None,
        reason: str = "Stock withdrawn",
    ) -> list[tuple[Batch, int]]:
        return self.withdraw(
            product_id,
            amount,
            reference_date=reference_date,
            reason=reason,
            batch_selection_policy=FefoBatchSelectionPolicy(),
        )

    def withdraw(
        self,
        product_id: str | int,
        amount: int,
        reference_date: date = None,
        reason: str = "Stock withdrawn",
        batch_selection_policy: BatchSelectionPolicy | None = None,
    ) -> list[tuple[Batch, int]]:
        if amount <= 0:
            raise ValueError("Quantidade para baixa deve ser positiva")
        if reference_date is None:
            reference_date = date.today()

        policy = batch_selection_policy or FefoBatchSelectionPolicy()
        batches = policy.order_batches(self.valid_batches_for(product_id, reference_date))

        available = sum(batch.current_amount for batch in batches)
        if available < amount:
            raise ValueError(
                f"Separação inválida para o produto '{product_id}'. "
                f"Necessário: {amount}, disponível em lotes válidos: {available}"
            )

        remaining = amount
        consumed: list[tuple[Batch, int]] = []
        for batch in batches:
            if remaining <= 0:
                break

            amount_to_remove = min(batch.current_amount, remaining)
            batch.consume_amount(amount_to_remove)
            movement = StockMovement(
                batch.product,
                MovementType.OUTBOUND,
                amount_to_remove,
                batch_id=batch.id,
                reason=reason,
            )
            self.register(movement)
            consumed.append((batch, amount_to_remove))
            remaining -= amount_to_remove

        return consumed

    def to_dict(self) -> dict:
        return {
            "batches": [batch.to_dict() for batch in self._batches],
            "movements": [movement.to_dict() for movement in self._movements],
        }
