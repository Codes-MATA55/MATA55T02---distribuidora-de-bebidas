from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass(frozen=True)
class EntityId:
    value: UUID = field(default_factory=uuid4)

    def __str__(self) -> str:
        return str(self.value)


class PedidoId(EntityId): pass
class FornecedorId(EntityId): pass
class BatchId(EntityId): pass
class ProdutoId(EntityId): pass
class MovimentacaoId(EntityId): pass
class ClienteId(EntityId): pass