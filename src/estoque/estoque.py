from collections import defaultdict
from typing import Optional
from ..bebida.bebida import Bebida
from ..exceptions.regras_negocio import EstoqueInsuficienteException
from .movimentacao import Movimentacao, TipoMovimentacao


class Estoque:
    """
    Gerencia o inventário de bebidas da distribuidora.

    Responsabilidades:
    - Controlar saldos por produto
    - Registrar toda movimentação (auditoria completa)
    - Proteger regras de negócio: não permite saldo negativo

    Design: não expõe os dicionários internos diretamente.
    Todo acesso é mediado por métodos com semântica de negócio.
    """

    def __init__(self) -> None:
        self._saldos: dict[str, int] = defaultdict(int)
        self._catalogo: dict[str, Bebida] = {}
        self._historico: list[Movimentacao] = []

    def registrar_produto(self, bebida: Bebida) -> None:
        """Adiciona um produto ao catálogo do estoque."""
        self._catalogo[bebida.id] = bebida

    def entrada(self, produto_id: str, quantidade: int, motivo: str = "Reposição") -> None:
        """Registra a entrada de produtos no estoque."""
        if quantidade <= 0:
            raise ValueError(f"Quantidade de entrada deve ser positiva. Recebido: {quantidade}")
        self._garantir_produto_existe(produto_id)
        self._saldos[produto_id] += quantidade
        self._registrar_movimentacao(produto_id, TipoMovimentacao.ENTRADA, quantidade, motivo)

    def saida(self, produto_id: str, quantidade: int, motivo: str = "Pedido") -> None:
        """Registra a saída de produtos do estoque."""
        if quantidade <= 0:
            raise ValueError(f"Quantidade de saída deve ser positiva. Recebido: {quantidade}")
        self._garantir_produto_existe(produto_id)
        disponivel = self._saldos[produto_id]
        if disponivel < quantidade:
            raise EstoqueInsuficienteException(produto_id, quantidade, disponivel)
        self._saldos[produto_id] -= quantidade
        self._registrar_movimentacao(produto_id, TipoMovimentacao.SAIDA, quantidade, motivo)

    def consultar_saldo(self, produto_id: str) -> int:
        """Retorna a quantidade disponível de um produto."""
        self._garantir_produto_existe(produto_id)
        return self._saldos[produto_id]

    def tem_saldo_suficiente(self, produto_id: str, quantidade: int) -> bool:
        """Verifica se há saldo suficiente sem lançar exceção."""
        if produto_id not in self._catalogo:
            return False
        return self._saldos[produto_id] >= quantidade

    def historico_produto(self, produto_id: str) -> list[Movimentacao]:
        """Retorna o histórico de movimentações de um produto."""
        return [m for m in self._historico if m.produto_id == produto_id]

    def historico_completo(self) -> list[Movimentacao]:
        """Retorna todo o histórico de movimentações."""
        return list(self._historico)

    def produto(self, produto_id: str) -> Optional[Bebida]:
        """Retorna o produto pelo ID, ou None se não existir."""
        return self._catalogo.get(produto_id)

    def resumo(self) -> dict[str, dict]:
        """Retorna um resumo do estoque atual."""
        resultado = {}
        for pid, bebida in self._catalogo.items():
            resultado[pid] = {
                "nome": bebida.nome,
                "categoria": bebida.categoria,
                "saldo": self._saldos[pid],
            }
        return resultado

    def _garantir_produto_existe(self, produto_id: str) -> None:
        if produto_id not in self._catalogo:
            raise KeyError(f"Produto '{produto_id}' não está registrado no estoque.")

    def _registrar_movimentacao(
        self,
        produto_id: str,
        tipo: TipoMovimentacao,
        quantidade: int,
        motivo: str,
    ) -> None:
        mov = Movimentacao(
            produto_id=produto_id,
            tipo=tipo,
            quantidade=quantidade,
            motivo=motivo,
        )
        self._historico.append(mov)
