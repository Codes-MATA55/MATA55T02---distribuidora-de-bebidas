from .usuario import Usuario, NivelAcesso


class Operador(Usuario):
    """
    Nível mais básico de acesso.
    Pode realizar separação e expedição, mas não cancelar pedidos.
    """

    @property
    def nivel_acesso(self) -> NivelAcesso:
        return NivelAcesso.OPERADOR


class Supervisor(Usuario):
    """
    Nível intermediário.
    Pode cancelar pedidos e gerar relatórios.
    """

    @property
    def nivel_acesso(self) -> NivelAcesso:
        return NivelAcesso.SUPERVISOR


class Gerente(Usuario):
    """
    Nível máximo de acesso.
    Pode realizar todas as operações, inclusive ajustes de estoque.
    """

    @property
    def nivel_acesso(self) -> NivelAcesso:
        return NivelAcesso.GERENTE

