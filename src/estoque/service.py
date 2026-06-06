from __future__ import annotations
from estoque.aggregate import Estoque
from estoque.repository import EstoqueRepository
from estoque.value_objects import Quantidade


class EstoqueService:
    def __init__(self, repository: EstoqueRepository):
        self._repository = repository

    # ------------------------------------------------------------------
    # Criação
    # ------------------------------------------------------------------

    def criar_estoque(self, produto_id: str) -> Estoque:
        if self._repository.buscar_por_produto(produto_id) is not None:
            raise ValueError(f"Já existe um estoque cadastrado para o produto '{produto_id}'.")
        estoque = Estoque.criar(produto_id)
        self._repository.salvar(estoque)
        return estoque

    # ------------------------------------------------------------------
    # Consultas
    # ------------------------------------------------------------------

    def buscar_por_produto(self, produto_id: str) -> Estoque:
        estoque = self._repository.buscar_por_produto(produto_id)
        if estoque is None:
            raise ValueError(f"Estoque não encontrado para o produto '{produto_id}'.")
        return estoque

    def buscar_por_id(self, estoque_id: str) -> Estoque:
        estoque = self._repository.buscar_por_id(estoque_id)
        if estoque is None:
            raise ValueError(f"Estoque com id '{estoque_id}' não encontrado.")
        return estoque

    def listar_todos(self) -> list[Estoque]:
        return self._repository.listar_todos()

    # ------------------------------------------------------------------
    # Operações de estoque
    # ------------------------------------------------------------------

    def repor(self, produto_id: str, quantidade: int) -> Estoque:
        estoque = self.buscar_por_produto(produto_id)
        estoque.repor(Quantidade(quantidade))
        self._repository.atualizar(estoque)
        return estoque

    def reservar(self, produto_id: str, quantidade: int) -> Estoque:
        estoque = self.buscar_por_produto(produto_id)
        estoque.reservar(Quantidade(quantidade))
        self._repository.atualizar(estoque)
        return estoque

    def efetuar_baixa_da_reserva(self, produto_id: str, quantidade: int) -> Estoque:
        """Confirma a saída definitiva do estoque (ex: pedido entregue)."""
        estoque = self.buscar_por_produto(produto_id)
        estoque.efetuar_baixa_da_reserva(Quantidade(quantidade))
        self._repository.atualizar(estoque)
        return estoque

    def cancelar_reserva(self, produto_id: str, quantidade: int) -> Estoque:
        """Cancela a reserva e devolve a quantidade ao disponível (ex: pedido cancelado)."""
        estoque = self.buscar_por_produto(produto_id)
        estoque.cancelar_reserva(Quantidade(quantidade))
        self._repository.atualizar(estoque)
        return estoque

    # ------------------------------------------------------------------
    # Exclusão
    # ------------------------------------------------------------------

    def excluir_estoque(self, estoque_id: str) -> None:
        estoque = self.buscar_por_id(estoque_id)
        if estoque.quantidade_reservada.valor > 0:
            raise ValueError(
                f"Não é possível excluir um estoque com reservas ativas "
                f"(reservado={estoque.quantidade_reservada})."
            )
        self._repository.excluir(estoque_id)
