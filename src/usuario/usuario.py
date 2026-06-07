from dataclasses import dataclass, field
from enum import Enum
from uuid import uuid4


class NivelAcesso(Enum):
    OPERADOR = 1
    SUPERVISOR = 2
    GERENTE = 3


@dataclass
class Usuario:
    """
    Classe base da hierarquia de usuarios.
    Sem autenticacao: apenas demonstra hierarquia e permissoes.
    """
    nome: str
    id: str = field(default_factory=lambda: str(uuid4()))

    @property
    def nivel_acesso(self) -> NivelAcesso:
        raise NotImplementedError

    def pode_cancelar_pedido(self) -> bool:
        return self.nivel_acesso.value >= NivelAcesso.SUPERVISOR.value

    def pode_aprovar_expedicao(self) -> bool:
        return self.nivel_acesso.value >= NivelAcesso.OPERADOR.value

    def pode_gerar_relatorio(self) -> bool:
        return self.nivel_acesso.value >= NivelAcesso.SUPERVISOR.value

    def pode_alterar_estoque(self) -> bool:
        return self.nivel_acesso.value >= NivelAcesso.GERENTE.value

    def __str__(self) -> str:
        return f"{self.__class__.__name__}(nome={self.nome!r})"