from typing import List

from domain.entities.movimentacao_estoque import StockMovement


class StockRegistry:
    def __init__(self):
        self._movements: List[StockMovement] = []

    def register(self, movement: StockMovement):
        self._movements.append(movement)

    def list_history(self) -> List[StockMovement]:
        return list(self._movements)
