from typing import Protocol, Sequence

from domain.entities.lote import Batch

class BatchSelectionPolicy(Protocol):
    def order_batches(self, batches: Sequence[Batch]) -> list[Batch]:
        pass

class FefoBatchSelectionPolicy:
    def order_batches(self, batches: Sequence[Batch]) -> list[Batch]:
        return sorted(batches, key=lambda batch: batch.expiration_date)

class LifoBatchSelectionPolicy:
    def order_batches(self, batches: Sequence[Batch]) -> list[Batch]:
        return sorted(batches, key=lambda batch: batch.expiration_date, reverse=True)
