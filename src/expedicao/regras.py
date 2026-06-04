from abc import ABC, abstractmethod
from ..pedido.pedido import Pedido
from ..estoque.estoque import Estoque
from ..exceptions.regras_negocio import RegraDeExpedicaoVioladaException


class RegraExpedicao(ABC):
    """
    Interface base para o Specification Pattern aplicado à expedição.

    Cada regra encapsula uma única verificação (SRP).
    Novas regras podem ser adicionadas sem modificar o código existente (OCP).
    """

    @abstractmethod
    def verificar(self, pedido: Pedido, estoque: Estoque) -> tuple[bool, str]:
        """
        Retorna (True, '') se a regra passa,
        ou (False, 'mensagem de erro') se a regra falha.
        """
        ...

    @property
    @abstractmethod
    def descricao(self) -> str:
        ...


class PedidoEstaSeparadoRegra(RegraExpedicao):
    """Regra: o pedido deve estar no estado 'Separado'."""

    @property
    def descricao(self) -> str:
        return "Pedido deve estar no estado 'Separado'"

    def verificar(self, pedido: Pedido, estoque: Estoque) -> tuple[bool, str]:
        if pedido.estado_atual != "Separado":
            return False, f"Estado atual é '{pedido.estado_atual}', esperado 'Separado'."
        return True, ""


class PedidoPossuiItensRegra(RegraExpedicao):
    """Regra: o pedido não pode estar vazio."""

    @property
    def descricao(self) -> str:
        return "Pedido deve conter ao menos um item"

    def verificar(self, pedido: Pedido, estoque: Estoque) -> tuple[bool, str]:
        if not pedido.itens:
            return False, "O pedido não possui itens."
        return True, ""


class TodosItensPresentesNoEstoqueRegra(RegraExpedicao):
    """
    Regra: todos os produtos do pedido devem existir no catálogo do estoque.
    (Verifica existência, não necessariamente saldo — a separação já garantiu isso.)
    """

    @property
    def descricao(self) -> str:
        return "Todos os produtos do pedido devem existir no catálogo"

    def verificar(self, pedido: Pedido, estoque: Estoque) -> tuple[bool, str]:
        ausentes = [
            item.bebida.nome
            for item in pedido.itens
            if estoque.produto(item.produto_id) is None
        ]
        if ausentes:
            return False, f"Produtos não encontrados no catálogo: {', '.join(ausentes)}"
        return True, ""


class ValidadorExpedicao:
    """
    Orquestrador das regras de expedição.
    Agrega múltiplas especificações e aplica todas de uma vez.

    Benefício: extensível sem modificação.
    Para adicionar nova regra: apenas instanciar ValidadorExpedicao com a nova regra.
    """

    def __init__(self, regras: list[RegraExpedicao] | None = None) -> None:
        self._regras = regras or self._regras_padrao()

    @staticmethod
    def _regras_padrao() -> list[RegraExpedicao]:
        return [
            PedidoPossuiItensRegra(),
            PedidoEstaSeparadoRegra(),
            TodosItensPresentesNoEstoqueRegra(),
        ]

    def validar(self, pedido: Pedido, estoque: Estoque) -> None:
        """
        Executa todas as regras.
        Lança RegraDeExpedicaoVioladaException com todas as violações encontradas.
        """
        violacoes = []
        for regra in self._regras:
            passou, mensagem = regra.verificar(pedido, estoque)
            if not passou:
                violacoes.append(f"[{regra.descricao}] {mensagem}")

        if violacoes:
            raise RegraDeExpedicaoVioladaException(violacoes)
