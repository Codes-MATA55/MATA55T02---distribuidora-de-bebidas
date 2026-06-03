from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from uuid import uuid4


class TipoMovimentacao(Enum):
    ENTRADA = auto()
    SAIDA = auto()


@dataclass(frozen=True)
class Movimentacao:
    """
    Representa um registro imutável de movimentação de estoque.
    Frozen=True garante que o histórico não seja alterado após o registro.
    """
    produto_id: str
    tipo: TipoMovimentacao
    quantidade: int
    motivo: str
    id: str = field(default_factory=lambda: str(uuid4()))
    timestamp: datetime = field(default_factory=datetime.now)

    def __str__(self) -> str:
        tipo_str = "ENTRADA" if self.tipo == TipoMovimentacao.ENTRADA else "SAÍDA"
        return (
            f"[{self.timestamp:%Y-%m-%d %H:%M:%S}] {tipo_str} | "
            f"Produto: {self.produto_id} | Qtd: {self.quantidade} | "
            f"Motivo: {self.motivo}"
        )
