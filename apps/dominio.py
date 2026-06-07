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
    VENDAS        = "vendas"
    ESTOQUE       = "estoque"


class TipoDesconto(str, Enum):
    """Estratégias de desconto aplicáveis a um cupom."""
    PERCENTUAL = "percentual"
    FIXO       = "fixo"


class StatusPedido(str, Enum):
    """Máquina de estados do ciclo de vida de um pedido."""
    ABERTO     = "aberto"
    CONFIRMADO = "confirmado"
    CANCELADO  = "cancelado"


class TipoVenda(str, Enum):
    """Modalidade de venda — individual ou em lote."""
    INDIVIDUAL = "individual"
    LOTE       = "lote"


# ─────────────────────────────────────────────────────────────
# PERMISSÕES — mapeamento declarativo por papel
# ─────────────────────────────────────────────────────────────

PERMISSOES: dict[TipoUsuario, set[str]] = {
    TipoUsuario.ADMINISTRADOR: {
        "bebida:criar", "bebida:editar", "bebida:remover", "bebida:listar",
        "categoria:criar", "categoria:editar", "categoria:remover", "categoria:listar",
        "estoque:adicionar", "estoque:remover", "estoque:listar",
        "venda:realizar", "venda:listar", "venda:cancelar",
        "cupom:criar", "cupom:editar", "cupom:remover", "cupom:listar",
        "usuario:criar", "usuario:editar", "usuario:remover", "usuario:listar",
        "relatorio:visualizar",
    },
    TipoUsuario.GERENCIA: {
        "bebida:criar", "bebida:editar", "bebida:listar",
        "categoria:criar", "categoria:editar", "categoria:listar",
        "estoque:adicionar", "estoque:listar",
        "venda:realizar", "venda:listar",
        "cupom:criar", "cupom:editar", "cupom:listar",
        "relatorio:visualizar",
    },
    TipoUsuario.VENDAS: {
        "bebida:listar",
        "categoria:listar",
        "estoque:listar",
        "venda:realizar", "venda:listar",
        "cupom:listar",
    },
    TipoUsuario.ESTOQUE: {
        "bebida:listar",
        "categoria:listar",
        "estoque:adicionar", "estoque:remover", "estoque:listar",
        "venda:listar",
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


@dataclass(frozen=True)
class PrecoUnitario:
    """Value Object que protege o valor monetário unitário."""
    valor: float

    def __post_init__(self):
        if self.valor < 0:
            raise ValueError(f"Preço não pode ser negativo. Recebido: {self.valor}")

    def aplicar_desconto_percentual(self, percentual: float) -> "PrecoUnitario":
        if not (0 <= percentual <= 100):
            raise ValueError("Percentual deve estar entre 0 e 100.")
        return PrecoUnitario(round(self.valor * (1 - percentual / 100), 2))

    def __str__(self) -> str:
        return f"R$ {self.valor:.2f}"


@dataclass(frozen=True)
class CodigoCupom:
    """Value Object para código de cupom — sempre maiúsculo e sem espaços."""
    codigo: str

    def __post_init__(self):
        limpo = self.codigo.strip().upper()
        if len(limpo) < 3:
            raise ValueError("Código do cupom deve ter ao menos 3 caracteres.")
        object.__setattr__(self, "codigo", limpo)

    def __str__(self) -> str:
        return self.codigo


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

    Composição: possui Volume e PrecoUnitario como Value Objects.
    Associação: referencia CategoriaBebida pelo id.
    """

    def __init__(
        self,
        nome: str,
        categoria_id: str,
        marca: str,
        volume_ml: int,
        preco_unitario: float,
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
        self.__preco = PrecoUnitario(preco_unitario)       # Value Object
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
    def preco(self) -> PrecoUnitario:
        return self.__preco

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
        preco_unitario: float = None,
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
        if preco_unitario is not None:
            self.__preco = PrecoUnitario(preco_unitario)
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
            "preco_unitario": self.__preco.valor,
            "teor_alcoolico": self.__teor_alcoolico,
            "fornecedor": self.__fornecedor,
            "ativo": self.__ativo,
            "criado_em": self.__criado_em.isoformat(),
            "atualizado_em": self.__atualizado_em.isoformat(),
        }

    def __repr__(self) -> str:
        return f"<Bebida id={self.__id} nome={self.__nome} preco={self.__preco}>"


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


class Cupom:
    """
    Entidade que representa um cupom de desconto.
    Encapsula regras de aplicação e validade.
    """

    def __init__(
        self,
        codigo: str,
        descricao: str,
        tipo_desconto: TipoDesconto,
        valor_desconto: float,
        valor_minimo_pedido: float,
        usos_maximos: int,
        valido_de: date,
        valido_ate: date,
        id: Optional[str] = None,
        usos_realizados: int = 0,
        ativo: bool = True,
        criado_em: Optional[datetime] = None,
    ):
        self.__id = id or f"cup-{uuid.uuid4().hex[:8]}"
        self.__codigo = CodigoCupom(codigo)                # Value Object
        self.__descricao = descricao
        self.__tipo_desconto = tipo_desconto
        self.__valor_desconto = valor_desconto
        self.__valor_minimo_pedido = valor_minimo_pedido
        self.__usos_maximos = usos_maximos
        self.__usos_realizados = usos_realizados
        self.__valido_de = valido_de
        self.__valido_ate = valido_ate
        self.__ativo = ativo
        self.__criado_em = criado_em or datetime.now()

    @property
    def id(self) -> str:
        return self.__id

    @property
    def codigo(self) -> str:
        return str(self.__codigo)

    @property
    def ativo(self) -> bool:
        return self.__ativo

    @property
    def usos_realizados(self) -> int:
        return self.__usos_realizados

    def esta_valido(self) -> bool:
        hoje = date.today()
        return (
            self.__ativo
            and self.__valido_de <= hoje <= self.__valido_ate
            and self.__usos_realizados < self.__usos_maximos
        )

    def calcular_desconto(self, valor_total: float) -> float:
        """Polimorfismo via tipo_desconto — cada estratégia calcula diferente."""
        if not self.esta_valido():
            raise ValueError(f"Cupom {self.codigo} inválido ou expirado.")
        if valor_total < self.__valor_minimo_pedido:
            raise ValueError(
                f"Valor mínimo para este cupom é R$ {self.__valor_minimo_pedido:.2f}."
            )
        if self.__tipo_desconto == TipoDesconto.PERCENTUAL:
            return round(valor_total * self.__valor_desconto / 100, 2)
        return min(self.__valor_desconto, valor_total)

    def registrar_uso(self):
        if not self.esta_valido():
            raise ValueError("Cupom não pode ser usado.")
        self.__usos_realizados += 1

    def desativar(self):
        self.__ativo = False

    def atualizar(
        self,
        descricao: str = None,
        valor_desconto: float = None,
        valor_minimo_pedido: float = None,
        usos_maximos: int = None,
        valido_ate: date = None,
        ativo: bool = None,
    ):
        if descricao is not None:
            self.__descricao = descricao
        if valor_desconto is not None:
            self.__valor_desconto = valor_desconto
        if valor_minimo_pedido is not None:
            self.__valor_minimo_pedido = valor_minimo_pedido
        if usos_maximos is not None:
            self.__usos_maximos = usos_maximos
        if valido_ate is not None:
            self.__valido_ate = valido_ate
        if ativo is not None:
            self.__ativo = ativo

    def para_dict(self) -> dict:
        return {
            "id": self.__id,
            "codigo": str(self.__codigo),
            "descricao": self.__descricao,
            "tipo_desconto": self.__tipo_desconto.value,
            "valor_desconto": self.__valor_desconto,
            "valor_minimo_pedido": self.__valor_minimo_pedido,
            "usos_maximos": self.__usos_maximos,
            "usos_realizados": self.__usos_realizados,
            "ativo": self.__ativo,
            "valido_de": self.__valido_de.isoformat(),
            "valido_ate": self.__valido_ate.isoformat(),
            "criado_em": self.__criado_em.isoformat(),
        }


@dataclass
class ItemPedido:
    """
    Composição de Pedido.
    Um ItemPedido não existe fora de um Pedido.
    Referência: Booch p.89 — composição.
    """
    bebida_id: str
    nome_bebida: str
    quantidade: int
    preco_unitario: float

    def __post_init__(self):
        if self.quantidade <= 0:
            raise ValueError("Quantidade do item deve ser positiva.")
        if self.preco_unitario < 0:
            raise ValueError("Preço unitário não pode ser negativo.")

    @property
    def subtotal(self) -> float:
        return round(self.quantidade * self.preco_unitario, 2)

    def para_dict(self) -> dict:
        return {
            "bebida_id": self.bebida_id,
            "nome_bebida": self.nome_bebida,
            "quantidade": self.quantidade,
            "preco_unitario": self.preco_unitario,
            "subtotal": self.subtotal,
        }


class Pedido:
    """
    Aggregate Root do contexto de vendas.
    Gerencia ciclo de vida, itens, cupom e cálculo de valor final.
    Referência: Evans DDD p.125
    """

    def __init__(
        self,
        usuario_id: str,
        tipo_venda: TipoVenda,
        id: Optional[str] = None,
        criado_em: Optional[datetime] = None,
    ):
        self.__id = id or f"ped-{uuid.uuid4().hex[:8]}"
        self.__usuario_id = usuario_id
        self.__tipo_venda = tipo_venda
        self.__itens: list[ItemPedido] = []
        self.__cupom: Optional[Cupom] = None
        self.__status = StatusPedido.ABERTO
        self.__criado_em = criado_em or datetime.now()
        self.__desconto_aplicado: float = 0.0

    @property
    def id(self) -> str:
        return self.__id

    @property
    def status(self) -> StatusPedido:
        return self.__status

    @property
    def valor_bruto(self) -> float:
        return round(sum(i.subtotal for i in self.__itens), 2)

    @property
    def desconto_aplicado(self) -> float:
        return self.__desconto_aplicado

    @property
    def valor_final(self) -> float:
        return round(self.valor_bruto - self.__desconto_aplicado, 2)

    def adicionar_item(self, item: ItemPedido):
        """Composição — o pedido controla seus itens."""
        if self.__status != StatusPedido.ABERTO:
            raise ValueError("Não é possível adicionar itens a um pedido fechado.")
        self.__itens.append(item)

    def aplicar_cupom(self, cupom: Cupom):
        """Aplica cupom e calcula desconto com todas as validações de negócio."""
        if self.__status != StatusPedido.ABERTO:
            raise ValueError("Cupom só pode ser aplicado em pedido aberto.")
        desconto = cupom.calcular_desconto(self.valor_bruto)
        self.__cupom = cupom
        self.__desconto_aplicado = desconto

    def confirmar(self):
        """Transição de estado — encapsulada no aggregate."""
        if self.__status != StatusPedido.ABERTO:
            raise ValueError("Apenas pedidos abertos podem ser confirmados.")
        if not self.__itens:
            raise ValueError("Pedido não pode ser confirmado sem itens.")
        self.__status = StatusPedido.CONFIRMADO
        if self.__cupom:
            self.__cupom.registrar_uso()

    def cancelar(self):
        if self.__status == StatusPedido.CANCELADO:
            raise ValueError("Pedido já está cancelado.")
        self.__status = StatusPedido.CANCELADO

    def para_dict(self) -> dict:
        return {
            "id": self.__id,
            "usuario_id": self.__usuario_id,
            "tipo_venda": self.__tipo_venda.value,
            "itens": [i.para_dict() for i in self.__itens],
            "cupom_codigo": str(self.__cupom.codigo) if self.__cupom else None,
            "valor_bruto": self.valor_bruto,
            "desconto_aplicado": self.__desconto_aplicado,
            "valor_final": self.valor_final,
            "status": self.__status.value,
            "criado_em": self.__criado_em.isoformat(),
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


class Vendedor(UsuarioBase):
    """Herança: foco em realizar e consultar vendas."""

    def __init__(self, **kwargs):
        super().__init__(tipo=TipoUsuario.VENDAS, **kwargs)


class Estoquista(UsuarioBase):
    """Herança: foco em movimentação de estoque."""

    def __init__(self, **kwargs):
        super().__init__(tipo=TipoUsuario.ESTOQUE, **kwargs)


# — Factory de usuários (padrão Factory Method) —
FACTORY_USUARIO: dict[TipoUsuario, type] = {
    TipoUsuario.ADMINISTRADOR: Administrador,
    TipoUsuario.GERENCIA: Gerente,
    TipoUsuario.VENDAS: Vendedor,
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
