# Defesa Técnica Parcial — AA3
## Distribuidora de Bebidas em Alta Escala

---

## 1. Evolução do Domínio

O projeto partiu de um problema comum em sistemas acadêmicos: criar um CRUD
com classes anêmicas. A decisão central foi ir na direção oposta — construir
um **domínio rico**, onde as regras de negócio vivem dentro dos objetos e não
em camadas externas de serviço.

### Ponto de partida (antes)

A versão ingênua do problema seria:

```python
# Abordagem anêmica — o que foi rejeitado
class Pedido:
    def __init__(self):
        self.status = "criado"
        self.itens = []

# Regra de negócio vazando para fora do domínio
if pedido.status == "separado":
    pedido.status = "em_expedicao"
```

Problemas dessa abordagem: qualquer parte do código pode alterar o status
diretamente, não há validação de transições, e as regras ficam espalhadas.

### Depois da evolução

```python
# Domínio rico — o que foi implementado
pedido.iniciar_expedicao()  # o próprio pedido decide se pode ou não
```

O `Pedido` delega ao seu estado atual, que sabe exatamente o que é permitido.
Transições inválidas lançam `TransicaoDeEstadoInvalidaException` sem nenhum
`if` externo.

---

## 2. Refatorações Realizadas

### 2.1 Função `main()` — de monolito a responsabilidade única

**Antes:** a função `main()` tinha mais de 200 linhas e 9 blocos de
responsabilidade diferentes, violando diretamente o SRP e causando erro de
complexidade no flake8 (`C901 'main' is too complex`).

```python
# Antes — tudo em uma função
def main() -> None:
    # configurar observers
    # criar produtos
    # abastecer estoque
    # demonstrar fluxo completo
    # demonstrar cancelamento
    # demonstrar transição inválida
    # demonstrar expedição bloqueada
    # demonstrar usuários
    # exibir métricas
    # 200+ linhas...
```

**Depois:** cada responsabilidade virou sua própria função com nome descritivo.

```python
def main() -> None:
    cerveja, refrigerante, suco = criar_catalogo()
    estoque = abastecer_estoque(cerveja, refrigerante, suco)
    event_bus, monitoramento = configurar_observers(estoque)
    demonstrar_fluxo_completo(cerveja, refrigerante, suco, estoque, event_bus)
    demonstrar_cancelamento(cerveja, event_bus)
    demonstrar_transicao_invalida(cerveja)
    demonstrar_expedicao_bloqueada(cerveja, estoque)
    demonstrar_usuarios()
    exibir_metricas(monitoramento, estoque)
```

A `main()` passou de 200 linhas para 9 — apenas orquestra, sem lógica.

### 2.2 `LoggerObserver` — remoção de efeito colateral

**Antes:** o `LoggerObserver` chamava `print()` dentro do `notificar()`,
acoplando o comportamento de log à saída padrão e poluindo o terminal durante
os testes.

```python
# Antes — efeito colateral indesejado
def notificar(self, evento: Evento) -> None:
    entrada = f"[{evento.timestamp}] {evento.tipo}: {evento.dados}"
    self._logs.append(entrada)
    print(f"LOG: {entrada}")  # ← poluía o terminal nos testes
```

**Depois:** o observer apenas armazena. Quem quiser exibir, chama
`obter_logs()`.

```python
# Depois — sem efeito colateral
def notificar(self, evento: Evento) -> None:
    entrada = (
        f"[{evento.timestamp:%Y-%m-%d %H:%M:%S}] "
        f"{evento.tipo}: {evento.dados}"
    )
    self._logs.append(entrada)
```

### 2.3 `FIFOSeparacao` — remoção de prints de debug

**Antes:** a separação imprimia no terminal o progresso de cada item,
acoplando a lógica de domínio à apresentação.

```python
# Antes
print(f"Separado: {item.bebida.nome} x{item.quantidade} (FIFO)")
print(f"Pedido {pedido.id[:8]} separado com sucesso via FIFO.")
```

**Depois:** a separação apenas executa e muda o estado. A apresentação fica
no `main.py`.

### 2.4 Testes — remoção do `sys.path` manual

**Antes:** todos os arquivos de teste manipulavam o `sys.path` manualmente,
causando erros `E402` no flake8.

```python
# Antes — em todos os arquivos de teste
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import unittest  # E402: import not at top of file
from src.bebida.cerveja import Cerveja  # E402
```

**Depois:** o `conftest.py` na raiz resolve o path uma única vez, e os
arquivos de teste ficam limpos.

```python
# Depois — arquivo de teste limpo
import unittest
from src.bebida.cerveja import Cerveja
from src.pedido.pedido import Pedido
```

---

## 3. Padrões Aplicados

### 3.1 State Pattern — ciclo de vida do Pedido

**Problema que resolve:** sem State Pattern, o código ficaria cheio de
condicionais para verificar o estado atual antes de cada operação.

**Como foi aplicado:** cada estado (`Criado`, `EmSeparacao`, `Separado`,
`EmExpedicao`, `Entregue`, `Cancelado`) é uma classe que sobrescreve apenas
os métodos que fazem sentido a partir daquele estado. O comportamento padrão
da classe base lança exceção.

**Benefício concreto:** adicionar um novo estado (ex: `EmRevisao`) exige
criar uma nova classe, sem tocar nos estados existentes.

### 3.2 Strategy Pattern — separação de pedidos

**Problema que resolve:** a distribuidora pode precisar de diferentes ordens
de separação dependendo do contexto (urgência, tipo de produto, cliente VIP).

**Como foi aplicado:** `EstrategiaSeparacao` define o contrato. `FIFOSeparacao`
implementa a estratégia padrão. O `main.py` injeta a estratégia na chamada.

**Benefício concreto:** para adicionar LIFO ou Prioridade, basta criar uma
nova classe que implementa `EstrategiaSeparacao`, sem alterar o `Pedido` ou
o `Estoque`.

### 3.3 Specification Pattern — regras de expedição

**Problema que resolve:** as regras de expedição podem crescer com o tempo
(horário permitido, limite de peso, restrição por região). Se fossem `if`s
dentro de um método, cresceriam indefinidamente.

**Como foi aplicado:** cada regra é uma classe com um método `verificar()`
que retorna `(bool, mensagem)`. O `ValidadorExpedicao` agrega e executa todas,
reportando **todas** as violações de uma vez — não apenas a primeira.

**Benefício concreto:** nova regra = nova classe. O validador não muda.

### 3.4 Observer Pattern — desacoplamento de efeitos

**Problema que resolve:** quando um pedido é entregue, várias coisas precisam
acontecer: baixa no estoque, geração de log, atualização de métricas. Se o
`Pedido` chamasse cada um diretamente, teria alto acoplamento com todos.

**Como foi aplicado:** o `Pedido` publica um `Evento` imutável no `EventBus`.
`LoggerObserver`, `MonitoramentoObserver` e `AtualizacaoEstoqueObserver`
reagem de forma independente.

**Benefício concreto:** adicionar notificação por e-mail ou geração de nota
fiscal não requer alterar uma linha do `Pedido`.

---

## 4. Padrões Rejeitados e Por Quê

### 4.1 Singleton para o Estoque

**Considerado:** usar Singleton para garantir uma única instância de `Estoque`
no sistema.

**Rejeitado porque:**
- Dificulta testes unitários — cada teste precisaria resetar o estado global
- Acopla todos os módulos a uma instância global implícita
- O problema é melhor resolvido por injeção de dependência: quem precisa do
  `Estoque` recebe uma instância via parâmetro

### 4.2 Repository Pattern para o histórico de movimentações

**Considerado:** criar um `MovimentacaoRepository` para separar o acesso ao
histórico da lógica de negócio do `Estoque`.

**Rejeitado porque:**
- O projeto não usa banco de dados (tudo em memória)
- Adicionaria uma camada de abstração sem benefício real neste contexto
- O `Estoque` já encapsula o histórico adequadamente com `historico_completo()`
  e `historico_produto()`

### 4.3 Builder para construção de Pedido

**Considerado:** usar Builder para construir pedidos com muitos itens de forma
fluente (`PedidoBuilder().cliente("X").item(cerveja, 10).item(suco, 5).build()`).

**Rejeitado porque:**
- A construção de um `Pedido` não é suficientemente complexa para justificar
  o padrão — o `dataclass` com `adicionar_item()` já resolve de forma legível
- Adicionaria uma classe extra sem reduzir complexidade real

### 4.4 Template Method para separação

**Considerado:** usar Template Method na `EstrategiaSeparacao` para definir
os passos fixos (validar, separar, finalizar) e deixar apenas a ordenação
como variável.

**Rejeitado porque:**
- O Strategy Pattern já resolve o problema com mais flexibilidade
- Template Method exigiria herança onde composição é mais adequada
- Estratégias futuras (ex: Urgente) podem ter passos completamente diferentes,
  o que quebraria a estrutura do Template Method

---

## 5. Fronteiras Arquiteturais

O projeto está organizado em módulos que **não se cruzam diretamente**:

```
src/
├── bebida/        → conhece apenas a si mesmo
├── estoque/       → conhece bebida (para catalogar)
├── pedido/        → conhece bebida e observadores (EventBus)
│   └── estados/   → conhece apenas pedido (referência interna)
├── separacao/     → conhece pedido e estoque
├── expedicao/     → conhece pedido e estoque
├── observadores/  → conhece estoque (AtualizacaoEstoqueObserver)
├── usuario/       → conhece apenas a si mesmo
└── exceptions/    → não conhece ninguém
```

**Regra de ouro:** `Pedido` nunca importa `Estoque` diretamente. A comunicação
entre eles é exclusivamente via eventos (`EventBus`). Isso significa que
trocar a implementação do `Estoque` não afeta o `Pedido`.

---

## 6. Análise Crítica do Design

Esta seção aponta **limitações reais e dívidas técnicas** do projeto atual.

### 6.1 Hierarquia de `Usuario` não protege operações

A hierarquia `Operador → Supervisor → Gerente` existe e define permissões
(`pode_cancelar_pedido()`, `pode_alterar_estoque()`), mas **nenhuma operação
do domínio verifica essas permissões na prática**.

```python
# Hoje — qualquer objeto pode cancelar, sem verificação
pedido.cancelar()

# O que deveria ser
def cancelar(self, solicitante: Usuario) -> None:
    if not solicitante.pode_cancelar_pedido():
        raise PermissaoNegadaException(solicitante.nome, "cancelar_pedido")
    self._estado.cancelar(self)
```

**Dívida técnica:** a hierarquia de usuários é decorativa. Em uma evolução
real, as operações do `Pedido` e do `Estoque` deveriam receber o `Usuario`
como parâmetro e verificar permissões.

### 6.2 `Movimentacao` é `frozen=True` mas não tem ID de pedido

O histórico de movimentações registra `produto_id`, `tipo`, `quantidade` e
`motivo`, mas **não rastreia qual pedido gerou a saída**. O `motivo` carrega
essa informação como string, o que não é rastreável programaticamente.

```python
# Hoje — rastreabilidade por string
motivo="Separacao FIFO - Pedido " + pedido.id[:8]

# O que seria melhor
pedido_id: Optional[str] = None  # campo estruturado
```

### 6.3 `EventBus` não tem persistência nem garantia de entrega

Se um `Observer` lançar uma exceção durante o `notificar()`, o `EventBus`
atual não tem tratamento de erro — a exceção se propaga e os demais observers
não recebem o evento.

```python
# Hoje — sem tratamento de falha
def publicar(self, evento: Evento) -> None:
    for obs in self._assinantes.get(evento.tipo, []):
        obs.notificar(evento)  # se lançar exceção, os próximos não executam
```

**Melhoria possível:** usar `try/except` por observer e logar falhas sem
interromper a cadeia.

### 6.4 Strategy de separação não tem rollback

Se a separação de um pedido com 3 itens falhar no segundo item, o primeiro
já foi deduzido do estoque. Hoje não há mecanismo de rollback.

```python
# Risco atual em FIFOSeparacao.separar()
for item in pedido.itens:
    estoque.saida(...)  # se o terceiro item falhar, os dois primeiros já saíram
```

**Solução possível:** implementar o padrão Unit of Work ou verificar
antecipadamente todos os saldos antes de deduzir qualquer item — o que foi
parcialmente feito em `_validar_disponibilidade()`, mas sem garantia de
atomicidade em ambiente concorrente.

### 6.5 Testes não cobrem o `main.py`

Os 89 testes cobrem o domínio isoladamente, mas o `main.py` — que demonstra
a integração de todos os módulos — não tem testes automatizados. Em um projeto
real, haveria testes de integração ou de aceitação cobrindo o fluxo completo.

---

## 7. Conclusão da Defesa

O projeto demonstra aplicação consciente de padrões de projeto, não como
fim em si, mas como resposta a problemas reais de design:

- **State** resolve o problema de transições condicionais espalhadas
- **Strategy** resolve o problema de algoritmos intercambiáveis
- **Specification** resolve o problema de regras de negócio composíveis
- **Observer** resolve o problema de acoplamento entre módulos

Os padrões rejeitados (Singleton, Repository, Builder, Template Method) foram
descartados por não trazerem benefício proporcional à complexidade que
introduziriam neste contexto específico.

As limitações apontadas na análise crítica são intencionais neste estágio —
representam decisões de escopo, não de ignorância. Em uma evolução futura,
a hierarquia de `Usuario` seria conectada às operações, o `EventBus` teria
resiliência, e o `Estoque` teria suporte a transações atômicas.
