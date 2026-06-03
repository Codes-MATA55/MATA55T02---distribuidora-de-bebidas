class RegraDeNegocioException(Exception):
    """Exceção base para violações de regras de negócio."""
    pass


class TransicaoDeEstadoInvalidaException(RegraDeNegocioException):
    """Lançada quando uma transição de estado inválida é tentada."""
    def __init__(self, estado_atual: str, estado_destino: str):
        super().__init__(
            f"Transição inválida: '{estado_atual}' → '{estado_destino}' não é permitida."
        )


class EstoqueInsuficienteException(RegraDeNegocioException):
    """Lançada quando não há estoque suficiente para uma operação."""
    def __init__(self, produto_id: str, quantidade_solicitada: int, quantidade_disponivel: int):
        super().__init__(
            f"Estoque insuficiente para o produto '{produto_id}'. "
            f"Solicitado: {quantidade_solicitada}, Disponível: {quantidade_disponivel}."
        )


class PedidoNaoEncontradoException(RegraDeNegocioException):
    """Lançada quando um pedido não é encontrado."""
    def __init__(self, pedido_id: str):
        super().__init__(f"Pedido '{pedido_id}' não encontrado.")


class RegraDeExpedicaoVioladaException(RegraDeNegocioException):
    """Lançada quando uma ou mais regras de expedição são violadas."""
    def __init__(self, violacoes: list[str]):
        mensagem = "Expedição bloqueada pelas seguintes regras:\n" + "\n".join(
            f"  - {v}" for v in violacoes
        )
        super().__init__(mensagem)
        self.violacoes = violacoes


class PermissaoNegadaException(RegraDeNegocioException):
    """Lançada quando um usuário não tem permissão para a operação."""
    def __init__(self, usuario: str, operacao: str):
        super().__init__(f"Usuário '{usuario}' não tem permissão para '{operacao}'.")
