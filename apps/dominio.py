"""
=============================================================
DOMÍNIO — Distribuidora de Bebidas em Alta Escala
=============================================================
Módulo central de Orientação a Objetos.

Princípios aplicados:
  - Encapsulamento: atributos privados com validação no construtor
  - Abstração: classes representam conceitos reais do negócio
  - Herança: UsuarioBase → tipos específicos de usuário
  - Polimorfismo: cada tipo de usuário responde a tem_permissao()
    de forma diferente
  - Composição: Pedido contém ItemPedido; Estoque contém Lote
  - Agregação: CategoriaBebida agrupa Bebidas independentes

Referências:
  Meyer - Object Oriented Software Construction, p.233
  Evans - Domain-Driven Design, p.4
  Booch - Object-Oriented Analysis and Design, p.89
=============================================================
"""

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, datetime
from enum import Enum
from typing import Optional
import uuid


# ─────────────────────────────────────────────────────────────
# ENUMERAÇÕES — tipagem forte no domínio (sem strings mágicas)
# ─────────────────────────────────────────────────────────────

class TipoUsuario(str, Enum):
    """Define os papéis disponíveis no sistema."""
    ADMINISTRADOR = "administrador"
    GERENCIA      = "gerencia"
    REQUISITANTE  = "requisitante"
    ESTOQUE       = "estoque"

class StatusPedido(str, Enum):
    """Define o ciclo de vida de uma requisição interna."""
    RASCUNHO  = "rascunho"
    PENDENTE  = "pendente"    # Aguardando separação/aprovação
    CONCLUIDO = "concluido"   # Estoque efetivamente baixado
    CANCELADO = "cancelado"

class MotivoPedido(str, Enum):
    """Substitui o tipo de venda por justificativas de saída."""
    ABASTECIMENTO = "abastecimento_interno"
    TRANSFERENCIA = "transferencia_filial"
    AVARIA        = "avaria_perda"
    REMANEJO      = "remanejo"


# ─────────────────────────────────────────────────────────────
# PERMISSÕES — mapeamento declarativo por papel
# ─────────────────────────────────────────────────────────────

PERMISSOES: dict[TipoUsuario, set[str]] = {
    TipoUsuario.ADMINISTRADOR: {
        "bebida:criar", "bebida:editar", "bebida:remover", "bebida:listar",
        "categoria:criar", "categoria:editar", "categoria:remover", "categoria:listar",
        "estoque:adicionar", "estoque:remover", "estoque:listar",
        "pedido:criar", "pedido:listar", "pedido:cancelar",  # <─── Atualizado
        "usuario:criar", "usuario:editar", "usuario:remover", "usuario:listar",
        "relatorio:visualizar",
    },
    TipoUsuario.GERENCIA: {
        "bebida:criar", "bebida:editar", "bebida:listar",
        "categoria:criar", "categoria:editar", "categoria:listar",
        "estoque:adicionar", "estoque:listar",
        "pedido:criar", "pedido:listar",                     # <─── Atualizado
        "relatorio:visualizar",
    },
    TipoUsuario.REQUISITANTE: {
        "bebida:listar",
        "categoria:listar",
        "estoque:listar",
        "pedido:criar", "pedido:listar",                     # <─── Novo papel dele
    },
    TipoUsuario.ESTOQUE: {
        "bebida:listar",
        "categoria:listar",
        "estoque:adicionar", "estoque:remover", "estoque:listar",
        "pedido:listar",                                      # <─── Pode auditar saídas
    },
}


# ─────────────────────────────────────────────────────────────
# VALUE OBJECTS — imutáveis, validados, sem identidade própria
# Referência: Evans DDD p.97 | Booch p.89
# ─────────────────────────────────────────────────────────────

@dataclass(frozen=True)
class Volume:
    """Value Object que representa volume em mililitros."""
    ml: int

    def __post_init__(self):
        if self.ml <= 0:
            raise ValueError(f"Volume deve ser positivo. Recebido: {self.ml}")

    def __str__(self) -> str:
        return f"{self.ml}ml" if self.ml < 1000 else f"{self.ml / 1000:.1f}L"



# ─────────────────────────────────────────────────────────────
# ENTIDADES
# Referência: Evans DDD p.89 | Meyer p.233
# ─────────────────────────────────────────────────────────────

class CategoriaBebida:
    """
    Entidade que classifica bebidas.
    Encapsula identidade e regras de negócio da categoria.
    """

    def __init__(
        self,
        nome: str,
        descricao: str,
        alcoolica: bool,
        id: Optional[str] = None,
        criado_em: Optional[datetime] = None,
    ):
        self.__id = id or f"cat-{uuid.uuid4().hex[:8]}"
        self.__nome = self.__validar_nome(nome)
        self.__descricao = descricao
        self.__alcoolica = alcoolica
        self.__criado_em = criado_em or datetime.now()

    # — Validação interna (encapsulamento) —
    @staticmethod
    def __validar_nome(nome: str) -> str:
        if not nome or len(nome.strip()) < 2:
            raise ValueError("Nome da categoria deve ter ao menos 2 caracteres.")
        return nome.strip()

    # — Propriedades somente-leitura —
    @property
    def id(self) -> str:
        return self.__id

    @property
    def nome(self) -> str:
        return self.__nome

    @property
    def descricao(self) -> str:
        return self.__descricao

    @property
    def alcoolica(self) -> bool:
        return self.__alcoolica

    @property
    def criado_em(self) -> datetime:
        return self.__criado_em

    def atualizar(self, nome: str = None, descricao: str = None, alcoolica: bool = None):
        """Mutação controlada — apenas pelo próprio objeto."""
        if nome is not None:
            self.__nome = self.__validar_nome(nome)
        if descricao is not None:
            self.__descricao = descricao
        if alcoolica is not None:
            self.__alcoolica = alcoolica

    def para_dict(self) -> dict:
        return {
            "id": self.__id,
            "nome": self.__nome,
            "descricao": self.__descricao,
            "alcoolica": self.__alcoolica,
            "criado_em": self.__criado_em.isoformat(),
        }

    def __repr__(self) -> str:
        return f"<CategoriaBebida id={self.__id} nome={self.__nome}>"


class Bebida:
    """
    Entidade principal do domínio.
    Representa um produto comercializado pela distribuidora.

    Composição: possui Volume como Value Objects.
    Associação: referencia CategoriaBebida pelo id.
    """

    def __init__(
        self,
        nome: str,
        categoria_id: str,
        marca: str,
        volume_ml: int,
        fornecedor: str,
        teor_alcoolico: Optional[float] = None,
        id: Optional[str] = None,
        ativo: bool = True,
        criado_em: Optional[datetime] = None,
        atualizado_em: Optional[datetime] = None,
    ):
        self.__id = id or f"beb-{uuid.uuid4().hex[:8]}"
        self.__nome = self.__validar_nome(nome)
        self.__categoria_id = categoria_id
        self.__marca = marca
        self.__volume = Volume(volume_ml)                  # Value Object
        self.__teor_alcoolico = teor_alcoolico
        self.__fornecedor = fornecedor
        self.__ativo = ativo
        self.__criado_em = criado_em or datetime.now()
        self.__atualizado_em = atualizado_em or datetime.now()

    @staticmethod
    def __validar_nome(nome: str) -> str:
        if not nome or len(nome.strip()) < 2:
            raise ValueError("Nome da bebida deve ter ao menos 2 caracteres.")
        return nome.strip()

    @property
    def id(self) -> str:
        return self.__id

    @property
    def nome(self) -> str:
        return self.__nome

    @property
    def categoria_id(self) -> str:
        return self.__categoria_id

    @property
    def marca(self) -> str:
        return self.__marca

    @property
    def volume(self) -> Volume:
        return self.__volume

    @property
    def teor_alcoolico(self) -> Optional[float]:
        return self.__teor_alcoolico

    @property
    def fornecedor(self) -> str:
        return self.__fornecedor

    @property
    def ativo(self) -> bool:
        return self.__ativo

    @property
    def criado_em(self) -> datetime:
        return self.__criado_em

    def atualizar(
        self,
        nome: str = None,
        marca: str = None,
        volume_ml: int = None,
        teor_alcoolico: float = None,
        fornecedor: str = None,
        categoria_id: str = None,
    ):
        if nome is not None:
            self.__nome = self.__validar_nome(nome)
        if marca is not None:
            self.__marca = marca
        if volume_ml is not None:
            self.__volume = Volume(volume_ml)
        if teor_alcoolico is not None:
            self.__teor_alcoolico = teor_alcoolico
        if fornecedor is not None:
            self.__fornecedor = fornecedor
        if categoria_id is not None:
            self.__categoria_id = categoria_id
        self.__atualizado_em = datetime.now()

    def desativar(self):
        """Remoção lógica — o objeto controla seu próprio ciclo de vida."""
        self.__ativo = False
        self.__atualizado_em = datetime.now()

    def para_dict(self) -> dict:
        return {
            "id": self.__id,
            "nome": self.__nome,
            "categoria_id": self.__categoria_id,
            "marca": self.__marca,
            "volume_ml": self.__volume.ml,
            "teor_alcoolico": self.__teor_alcoolico,
            "fornecedor": self.__fornecedor,
            "ativo": self.__ativo,
            "criado_em": self.__criado_em.isoformat(),
            "atualizado_em": self.__atualizado_em.isoformat(),
        }

    def __repr__(self) -> str:
        return f"<Bebida id={self.__id} nome={self.__nome} marca={self.__marca}>"
    
class Pedido:
    """Entidade do Domínio: Representa o pedido de movimentação de estoque."""

    def __init__(
        self,
        usuario_id: str,
        motivo: MotivoPedido,
        id: Optional[str] = None,
        criado_em: Optional[datetime] = None,
        status: StatusPedido = StatusPedido.RASCUNHO
    ):
        self.__id = id or str(uuid.uuid4())
        self.__usuario_id = usuario_id  # Quem solicitou
        # Coerção defensiva: aceita tanto o Enum quanto a string equivalente
        self.__motivo = motivo if isinstance(motivo, MotivoPedido) else MotivoPedido(motivo)
        self.__criado_em = criado_em or datetime.now()
        self.__status = status if isinstance(status, StatusPedido) else StatusPedido(status)
        self.__itens: list[ItemPedido] = []

    # — Propriedades somente-leitura —
    @property
    def id(self) -> str:
        return self.__id

    @property
    def usuario_id(self) -> str:
        return self.__usuario_id

    @property
    def motivo(self) -> MotivoPedido:
        return self.__motivo

    @property
    def criado_em(self) -> datetime:
        return self.__criado_em

    @property
    def status(self) -> StatusPedido:
        return self.__status

    @property
    def itens(self) -> list[ItemPedido]:
        return self.__itens.copy()  # Encapsulamento: evita modificação externa direta

    def adicionar_item(self, item: ItemPedido):
        if self.__status != StatusPedido.RASCUNHO:
            raise ValueError("Não é possível modificar um pedido que não está em rascunho.")
        self.__itens.append(item)

    def confirmar(self):
        """Muda o status para concluído quando o estoque é retirado."""
        if not self.__itens:
            raise ValueError("Não é possível concluir um pedido sem itens.")
        if self.__status != StatusPedido.RASCUNHO:
            raise ValueError("Apenas pedidos em rascunho podem ser concluídos.")
        self.__status = StatusPedido.CONCLUIDO

    def cancelar(self):
        if self.__status == StatusPedido.CONCLUIDO:
            raise ValueError("Não é possível cancelar um pedido já concluído e retirado.")
        if self.__status == StatusPedido.CANCELADO:
            raise ValueError("Pedido já está cancelado.")
        self.__status = StatusPedido.CANCELADO

    def para_dict(self) -> dict:
        """"Mapeador para exportação de dados (utilizado nos repositórios)."""
        return {
            "id": self.__id,
            "usuario_id": self.__usuario_id,
            "motivo": self.__motivo.value,
            "status": self.__status.value,
            "criado_em": self.__criado_em.isoformat(),
            "itens": [item.para_dict() for item in self.__itens],
        }

    @classmethod
    def reconstruir(
        cls,
        usuario_id: str,
        motivo: MotivoPedido,
        id: str,
        criado_em: datetime,
        status: StatusPedido,
        itens: list["ItemPedido"],
    ) -> "Pedido":
        """
        Reconstitui um Pedido a partir de dados já persistidos (ex: vindos do JSON).

        Diferente do fluxo normal (criar pedido vazio + adicionar_item),
        aqui os itens já existentes são restaurados diretamente, sem passar
        pelas regras de adicionar_item() — que exigem status RASCUNHO.
        Isso porque estamos representando um estado já válido no passado,
        não realizando uma nova operação de negócio.
        """
        pedido = cls(
            usuario_id=usuario_id,
            motivo=motivo,
            id=id,
            criado_em=criado_em,
            status=status,
        )
        pedido.__itens = list(itens)
        return pedido

    def __repr__(self) -> str:
        return f"<Pedido id={self.__id} status={self.__status.value} itens={len(self.__itens)}>"

@dataclass(frozen=True)
class ItemPedido:
    """
    Composição de Pedido.
    Um ItemPedido não existe fora de um Pedido.
    Referência: Booch p.89 — composição.

    Imutável (frozen): garante que a invariante validada no
    __post_init__ (quantidade > 0) não pode ser quebrada depois
    da criação do objeto.
    """
    bebida_id: str
    nome_bebida: str
    quantidade: int

    def __post_init__(self):
        if self.quantidade <= 0:
            raise ValueError("Quantidade do item deve ser positiva.")

    def para_dict(self) -> dict:
        return {
            "bebida_id": self.bebida_id,
            "nome_bebida": self.nome_bebida,
            "quantidade": self.quantidade,
        }

class Lote:
    """
    Entidade que representa um lote físico de bebida.
    Composição com Estoque — um lote não existe fora do contexto de estoque.
    """

    def __init__(
        self,
        bebida_id: str,
        quantidade: int,
        data_fabricacao: date,
        data_validade: date,
        codigo_lote: str,
        id: Optional[str] = None,
        quantidade_disponivel: Optional[int] = None,
        criado_em: Optional[datetime] = None,
    ):
        if quantidade <= 0:
            raise ValueError("Quantidade do lote deve ser positiva.")
        if data_validade <= data_fabricacao:
            raise ValueError("Data de validade deve ser posterior à fabricação.")

        self.__id = id or f"lot-{uuid.uuid4().hex[:8]}"
        self.__bebida_id = bebida_id
        self.__quantidade = quantidade
        self.__quantidade_disponivel = quantidade_disponivel if quantidade_disponivel is not None else quantidade
        self.__data_fabricacao = data_fabricacao
        self.__data_validade = data_validade
        self.__codigo_lote = codigo_lote
        self.__criado_em = criado_em or datetime.now()

    @property
    def id(self) -> str:
        return self.__id

    @property
    def bebida_id(self) -> str:
        return self.__bebida_id

    @property
    def quantidade(self) -> int:
        return self.__quantidade

    @property
    def quantidade_disponivel(self) -> int:
        return self.__quantidade_disponivel

    @property
    def data_validade(self) -> date:
        return self.__data_validade

    @property
    def codigo_lote(self) -> str:
        return self.__codigo_lote

    @property
    def esta_vencido(self) -> bool:
        return date.today() > self.__data_validade

    def atualizar(
        self,
        data_fabricacao: date = None,
        data_validade: date = None,
        codigo_lote: str = None,
    ):
        nova_fabricacao = data_fabricacao if data_fabricacao is not None else self.__data_fabricacao
        nova_validade = data_validade if data_validade is not None else self.__data_validade
        if nova_validade <= nova_fabricacao:
            raise ValueError("Data de validade deve ser posterior à fabricação.")
        self.__data_fabricacao = nova_fabricacao
        self.__data_validade = nova_validade
        if codigo_lote is not None:
            self.__codigo_lote = codigo_lote

    def baixar(self, qtd: int):
        """Reduz estoque disponível — invariante protegida."""
        if qtd <= 0:
            raise ValueError("Quantidade a baixar deve ser positiva.")
        if qtd > self.__quantidade_disponivel:
            raise ValueError(
                f"Estoque insuficiente no lote {self.__codigo_lote}. "
                f"Disponível: {self.__quantidade_disponivel}, Solicitado: {qtd}"
            )
        self.__quantidade_disponivel -= qtd

    def para_dict(self) -> dict:
        return {
            "id": self.__id,
            "bebida_id": self.__bebida_id,
            "quantidade": self.__quantidade,
            "quantidade_disponivel": self.__quantidade_disponivel,
            "data_fabricacao": self.__data_fabricacao.isoformat(),
            "data_validade": self.__data_validade.isoformat(),
            "codigo_lote": self.__codigo_lote,
            "criado_em": self.__criado_em.isoformat(),
        }


class Estoque:
    """
    Aggregate Root que guarda consistência do estoque de uma bebida.
    Referência: Evans DDD p.125 — aggregate boundary.
    """

    def __init__(self, bebida_id: str, quantidade_reservada: int = 0):
        self.__bebida_id = bebida_id
        self.__lotes: list[Lote] = []
        self.__quantidade_reservada = quantidade_reservada

    @property
    def bebida_id(self) -> str:
        return self.__bebida_id

    @property
    def quantidade_total(self) -> int:
        return sum(l.quantidade_disponivel for l in self.__lotes if not l.esta_vencido)

    @property
    def quantidade_disponivel(self) -> int:
        return self.quantidade_total - self.__quantidade_reservada

    def adicionar_lote(self, lote: Lote):
        if lote.bebida_id != self.__bebida_id:
            raise ValueError("Lote não pertence a esta bebida.")
        self.__lotes.append(lote)

    def baixar(self, quantidade: int):
        """Baixa do estoque respeitando FEFO (First Expired, First Out)."""
        if quantidade > self.quantidade_disponivel:
            raise ValueError(
                f"Estoque insuficiente. Disponível: {self.quantidade_disponivel}, "
                f"Solicitado: {quantidade}"
            )
        restante = quantidade
        lotes_validos = sorted(
            [l for l in self.__lotes if not l.esta_vencido and l.quantidade_disponivel > 0],
            key=lambda l: l.data_validade
        )
        for lote in lotes_validos:
            if restante == 0:
                break
            baixar_agora = min(restante, lote.quantidade_disponivel)
            lote.baixar(baixar_agora)
            restante -= baixar_agora

    def para_dict(self) -> dict:
        return {
            "bebida_id": self.__bebida_id,
            "quantidade_total": self.quantidade_total,
            "quantidade_reservada": self.__quantidade_reservada,
            "quantidade_disponivel": self.quantidade_disponivel,
            "atualizado_em": datetime.now().isoformat(),
        }


# ─────────────────────────────────────────────────────────────
# HIERARQUIA DE USUÁRIOS — Herança + Polimorfismo
# Referência: Booch p.620 | Meyer p.233
# ─────────────────────────────────────────────────────────────

class UsuarioBase:
    """
    Classe pai da hierarquia de usuários.
    Define o contrato comum e delega permissões ao subtipo.
    Herança: cada subclasse especializa tem_permissao().
    """

    def __init__(
        self,
        nome: str,
        login: str,
        senha_uid: str,
        tipo: TipoUsuario,
        id: Optional[str] = None,
        ativo: bool = True,
        criado_em: Optional[datetime] = None,
    ):
        self.__id = id or f"usr-{uuid.uuid4().hex[:8]}"
        self.__nome = nome
        self.__login = login
        self.__senha_uid = senha_uid   # encapsulada — nunca exposta diretamente
        self._tipo = tipo
        self.__ativo = ativo
        self.__criado_em = criado_em or datetime.now()

    @property
    def id(self) -> str:
        return self.__id

    @property
    def nome(self) -> str:
        return self.__nome

    @property
    def login(self) -> str:
        return self.__login

    @property
    def tipo(self) -> TipoUsuario:
        return self._tipo

    @property
    def ativo(self) -> bool:
        return self.__ativo

    def verificar_senha(self, senha_uid: str) -> bool:
        """Encapsulamento: comparação interna, senha nunca sai do objeto."""
        return self.__ativo and self.__senha_uid == senha_uid

    def tem_permissao(self, permissao: str) -> bool:
        """Polimorfismo: cada subclasse herda e pode sobrescrever."""
        return permissao in PERMISSOES.get(self._tipo, set())

    def atualizar(self, nome: str = None, tipo: str = None):
        if nome is not None:
            if not nome or len(nome.strip()) < 2:
                raise ValueError("Nome deve ter ao menos 2 caracteres.")
            self.__nome = nome.strip()
        if tipo is not None:
            self._tipo = TipoUsuario(tipo)

    def desativar(self):
        self.__ativo = False

    def para_dict(self) -> dict:
        return {
            "id": self.__id,
            "nome": self.__nome,
            "login": self.__login,
            "tipo": self._tipo.value,
            "ativo": self.__ativo,
            "criado_em": self.__criado_em.isoformat(),
        }

    def __repr__(self) -> str:
        return f"<{self.__class__.__name__} login={self.__login} tipo={self._tipo.value}>"


class Administrador(UsuarioBase):
    """Herança: especializa UsuarioBase com acesso total."""

    def __init__(self, **kwargs):
        super().__init__(tipo=TipoUsuario.ADMINISTRADOR, **kwargs)


class Gerente(UsuarioBase):
    """Herança: acesso gerencial amplo, sem gestão de usuários."""

    def __init__(self, **kwargs):
        super().__init__(tipo=TipoUsuario.GERENCIA, **kwargs)

class Requisitante(UsuarioBase):
    """Herança: foco em realizar pedidos."""

    def __init__(self, **kwargs):
        super().__init__(tipo=TipoUsuario.REQUISITANTE, **kwargs)


class Estoquista(UsuarioBase):
    """Herança: foco em movimentação de estoque."""

    def __init__(self, **kwargs):
        super().__init__(tipo=TipoUsuario.ESTOQUE, **kwargs)


# — Factory de usuários (padrão Factory Method) —
FACTORY_USUARIO: dict[TipoUsuario, type] = {
    TipoUsuario.ADMINISTRADOR: Administrador,
    TipoUsuario.GERENCIA: Gerente,
    TipoUsuario.REQUISITANTE: Requisitante,
    TipoUsuario.ESTOQUE: Estoquista,
}


def criar_usuario(tipo: str, **kwargs) -> UsuarioBase:
    """
    Factory Method para instanciar o tipo correto de usuário.
    Referência: Head First Design Patterns p.646
    """
    try:
        tipo_enum = TipoUsuario(tipo)
    except ValueError:
        raise ValueError(f"Tipo de usuário inválido: {tipo}")
    cls = FACTORY_USUARIO[tipo_enum]
    return cls(**kwargs)