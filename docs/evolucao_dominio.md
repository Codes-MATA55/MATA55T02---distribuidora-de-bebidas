# Evolução do Domínio — Distribuidora de Bebidas

Documento de entrega referente à atividade avaliativa: **proteção de invariantes,
transições válidas e inválidas, testes e revisão de responsabilidades entre objetos.**

---

## 1. Proteção de Invariantes

Invariantes são regras que devem ser **sempre verdadeiras** para um objeto, em
qualquer ponto do seu ciclo de vida. No projeto, elas são protegidas no
`__post_init__` das dataclasses ou nos métodos de mutação — nunca verificadas
externamente.

### 1.1 Hierarquia de Bebidas (`src/bebida/`)

A classe abstrata `Bebida` valida atributos comuns a qualquer bebida:

- `volume_ml` deve ser positivo
- `preco_unitario` não pode ser negativo
- `nome` não pode ser vazio ou conter apenas espaços

```python
def _validar(self) -> None:
    if self.volume_ml <= 0:
        raise ValueError(
            f"Volume deve ser positivo. Recebido: {self.volume_ml}"
        )
    if self.preco_unitario < 0:
        raise ValueError(
            f"Preco nao pode ser negativo. Recebido: {self.preco_unitario}"
        )
    if not self.nome or not self.nome.strip():
        raise ValueError("Nome da bebida nao pode ser vazio.")
```

A classe `Suco` adiciona sua própria invariante: `percentual_polpa` deve estar
entre 0% e 100%.

### 1.2 Item de Pedido (`src/pedido/item_pedido.py`)

`ItemPedido` é uma dataclass `frozen=True` (imutável) que valida no construtor:

- `quantidade` deve ser maior que zero

```python
def __post_init__(self) -> None:
    if self.quantidade <= 0:
        raise ValueError(
            f"Quantidade deve ser positiva. Recebido: {self.quantidade}"
        )
```

### 1.3 Estoque (`src/estoque/estoque.py`)

O `Estoque` protege a invariante mais crítica do domínio: **o saldo nunca pode
ficar negativo**.

```python
def saida(self, produto_id: str, quantidade: int, motivo: str = "Pedido") -> None:
    if quantidade <= 0:
        raise ValueError(
            f"Quantidade de saida deve ser positiva. Recebido: {quantidade}"
        )
    self._garantir_produto_existe(produto_id)
    disponivel = self._saldos[produto_id]
    if disponivel < quantidade:
        raise EstoqueInsuficienteException(produto_id, quantidade, disponivel)
    self._saldos[produto_id] -= quantidade
    self._registrar_movimentacao(
        produto_id, TipoMovimentacao.SAIDA, quantidade, motivo
    )
```

Toda movimentação (`Movimentacao`) também é uma dataclass `frozen=True`,
garantindo que o histórico de auditoria não pode ser alterado após criado.

---

## 2. Transições Válidas e Inválidas (State Pattern)

O ciclo de vida do `Pedido` é controlado por **State Pattern**
(`src/pedido/estados/`). Cada estado concreto sabe exatamente quais transições
são permitidas a partir dele — não existe nenhum `if status == "..."` espalhado
pelo código.

### 2.1 Transições válidas

```
Criado ──────────────► EmSeparacao ──────────────► Separado
  │                         │                          │
  │                         │                          ▼
  └──────► Cancelado ◄──────┘                    EmExpedicao
                                                        │
                                                        ▼
                                                    Entregue
```

| De | Para | Método |
|---|---|---|
| `Criado` | `EmSeparacao` | `iniciar_separacao()` |
| `EmSeparacao` | `Separado` | `finalizar_separacao()` |
| `Separado` | `EmExpedicao` | `iniciar_expedicao()` |
| `EmExpedicao` | `Entregue` | `confirmar_entrega()` |
| `Criado` | `Cancelado` | `cancelar()` |
| `EmSeparacao` | `Cancelado` | `cancelar()` |

### 2.2 Transições inválidas

Cada classe de estado herda de `EstadoPedido`, que define **todas** as
transições possíveis como inválidas por padrão:

```python
class EstadoPedido(ABC):
    def iniciar_separacao(self, pedido: "Pedido") -> None:
        self._transicao_invalida("iniciar_separacao")

    def finalizar_separacao(self, pedido: "Pedido") -> None:
        self._transicao_invalida("finalizar_separacao")

    def iniciar_expedicao(self, pedido: "Pedido") -> None:
        self._transicao_invalida("iniciar_expedicao")

    def confirmar_entrega(self, pedido: "Pedido") -> None:
        self._transicao_invalida("confirmar_entrega")

    def cancelar(self, pedido: "Pedido") -> None:
        self._transicao_invalida("cancelar")

    def _transicao_invalida(self, operacao: str) -> None:
        from ...exceptions.regras_negocio import TransicaoDeEstadoInvalidaException
        raise TransicaoDeEstadoInvalidaException(self.nome, operacao)
```

Cada estado concreto **sobrescreve apenas os métodos que faz sentido permitir**.
Por exemplo, `Separado` só sobrescreve `iniciar_expedicao` — qualquer outra
chamada (`cancelar`, `confirmar_entrega`, etc.) cai no comportamento padrão e
lança `TransicaoDeEstadoInvalidaException`.

```python
class Separado(EstadoPedido):
    @property
    def nome(self) -> str:
        return "Separado"

    def iniciar_expedicao(self, pedido: "Pedido") -> None:
        from .em_expedicao import EmExpedicao
        pedido._mudar_estado(EmExpedicao())
```

### 2.3 Proteção contra mutação direta

O `Pedido` **não expõe setters de status**. A única forma de mudar o estado é
através dos métodos de negócio (`iniciar_separacao()`, `cancelar()`, etc.), que
delegam ao estado atual:

```python
# Impossível — não existe esse atributo público
pedido.status = "ENTREGUE"

# Correto — o domínio decide se a transição é válida
pedido.confirmar_entrega()
```

---

## 3. Testes

A suíte de testes (`tests/`, executada com `unittest`) cobre:

| Arquivo | Cobertura |
|---|---|
| `test_estados.py` | Todas as transições válidas, todas as inválidas, histórico completo de estados, estados terminais (`Entregue`, `Cancelado`) não aceitam novas transições |
| `test_estoque.py` | Entradas, saídas, saldo insuficiente, quantidades negativas, histórico imutável |
| `test_separacao_expedicao.py` | Estratégia FIFO, dedução de estoque, regras de expedição (Specification Pattern) |
| `test_bebidas_e_observers.py` | Invariantes de `Cerveja`, `Refrigerante`, `Suco`, `ItemPedido`, e o Observer Pattern (EventBus, Logger, Monitoramento) |

Para executar:

```bash
python -m unittest discover -s tests -v
```

Exemplo de teste de transição inválida:

```python
def test_criado_nao_pode_ir_para_entregue(self):
    p = _pedido_com_item()
    with self.assertRaises(TransicaoDeEstadoInvalidaException):
        p.confirmar_entrega()
```

Exemplo de teste de invariante de estoque:

```python
def test_saida_com_estoque_insuficiente_lanca_excecao(self):
    self.estoque.entrada(self.cerveja.id, 10, "Pouco")
    with self.assertRaises(EstoqueInsuficienteException):
        self.estoque.saida(self.cerveja.id, 11, "Demais")
```

---

## 4. Revisão de Responsabilidades entre Objetos

Cada classe do domínio tem **uma única razão para mudar** (Single
Responsibility Principle):

| Classe | Responsabilidade | NÃO faz |
|---|---|---|
| `Bebida` e subclasses | Representar um produto e validar seus dados | Não conhece estoque, pedido ou expedição |
| `Pedido` | Gerenciar seu próprio ciclo de vida e itens | Não sabe como separar ou expedir |
| `EstadoPedido` (e subclasses) | Decidir quais transições são válidas | Não acessa estoque nem dispara separação |
| `Estoque` | Controlar saldos e histórico de movimentações | Não sabe que pedidos existem |
| `FIFOSeparacao` (Strategy) | Decidir a ordem de separação dos itens | Não decide se o pedido pode ser expedido |
| `ValidadorExpedicao` (Specification) | Decidir se um pedido pode ser expedido | Não executa a expedição, só valida |
| `EventBus` / `Observer`s | Notificar interessados sobre eventos de domínio | Não conhecem a lógica interna de quem publica ou de quem escuta |

### 4.1 Colaboração sem acoplamento direto

O exemplo mais claro de baixo acoplamento é a atualização de estoque após uma
entrega. O `Pedido` **não conhece** o `Estoque`:

```python
def confirmar_entrega(self) -> None:
    self._estado.confirmar_entrega(self)
    self._publicar_evento("PEDIDO_ENTREGUE")
```

O `AtualizacaoEstoqueObserver` está inscrito no evento `PEDIDO_ENTREGUE` e reage
de forma independente:

```python
class AtualizacaoEstoqueObserver(Observer):
    def __init__(self, estoque: Estoque) -> None:
        self._estoque = estoque

    def notificar(self, evento: Evento) -> None:
        if evento.tipo != "PEDIDO_ENTREGUE":
            return
        # ... dá baixa no estoque
```

Isso significa que é possível adicionar um novo observador (ex: envio de
e-mail, geração de nota fiscal) **sem alterar uma linha** do `Pedido` ou do
`Estoque` — cumprindo o Princípio Aberto/Fechado (OCP).

---

## 5. Conclusão

A evolução do domínio se deu por meio de:

1. Validações no construtor de cada entidade (invariantes de estado)
2. State Pattern para eliminar `if/elif` de transição e centralizar as regras
3. Strategy Pattern para a estratégia de separação (extensível para LIFO,
   Prioridade, Urgente)
4. Specification Pattern para as regras de expedição (extensível para novas
   regras sem alterar código existente)
5. Observer Pattern para desacoplar efeitos colaterais (estoque, logging,
   monitoramento) da lógica principal do pedido
