from __future__ import annotations
from typing import Dict, Optional

from estoque.aggregate import Estoque


class EstoqueRepository:
    def __init__(self):
        self._estoques: Dict[str, Estoque] = {}

    def buscar_por_produto(self, produto_id: str) -> Optional[Estoque]:
        return next(
            (e for e in self._estoques.values() if e.produto_id == produto_id),
            None,
        )

    def salvar(self, estoque: Estoque) -> None:
        self._estoques[estoque.id] = estoque
