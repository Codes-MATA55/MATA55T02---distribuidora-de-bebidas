from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass(frozen=True)
class EntityId:
    valor: UUID = field(default_factory=uuid4)

    def __str__(self) -> str:
        return str(self.valor)


class PedidoId(EntityId): pass
class FornecedorId(EntityId): pass
class LoteId(EntityId): pass
class ProdutoId(EntityId): pass
class RegistroEstoqueId(EntityId): pass
class SeparacaoId(EntityId): pass