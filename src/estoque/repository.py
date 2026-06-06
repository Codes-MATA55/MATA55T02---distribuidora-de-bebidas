from __future__ import annotations
from typing import Dict, List, Optional
from estoque.aggregate import Estoque


class EstoqueRepository:
    def __init__(self):
        self._estoques: Dict[str, Estoque] = {}

    def buscar_por_id(self, estoque_id: str) -> Optional[Estoque]:
        return self._estoques.get(estoque_id)

    def buscar_por_produto(self, produto_id: str) -> Optional[Estoque]:
        return next(
            (e for e in self._estoques.values() if e.produto_id == produto_id),
            None,
        )

    def listar_todos(self) -> List[Estoque]:
        return list(self._estoques.values())

    def salvar(self, estoque: Estoque) -> None:
        self._estoques[estoque.id] = estoque

    def atualizar(self, estoque: Estoque) -> None:
        if estoque.id not in self._estoques:
            raise ValueError(f"Estoque com id '{estoque.id}' não encontrado para atualização.")
        self._estoques[estoque.id] = estoque

    def excluir(self, estoque_id: str) -> None:
        if estoque_id not in self._estoques:
            raise ValueError(f"Estoque com id '{estoque_id}' não encontrado para exclusão.")
        del self._estoques[estoque_id]
