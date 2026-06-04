# Proposta de DDD — Distribuidora de Bebidas em Alta Escala

## 1. Objetivo da proposta

O projeto prático consiste no desenvolvimento de um sistema para uma **Distribuidora de Bebidas em Alta Escala**.

O objetivo principal **não é criar um CRUD de bebidas**, mas modelar o domínio usando **Orientação a Objetos** e **DDD** para:

- proteger regras de negócio;
- facilitar manutenção;
- permitir evolução;
- tornar o sistema testável;
- organizar responsabilidades entre objetos.

O sistema deve trabalhar com:

- pedidos;
- estoque;
- separação;
- expedição;
- movimentações;
- estados do pedido;
- usuários;
- hierarquia de permissões;
- colaboração entre objetos.

Não será utilizado banco de dados. Os dados serão mantidos **em memória**, com repositórios simples e dados mockados quando necessário.

### Volumes de referência do domínio

- 50 mil cervejas por dia;
- 30 mil refrigerantes por dia;
- 100 mil sucos por dia.

---

## 2. DDD Estratégico

### 2.1 Subdomínios

A distribuidora possui várias operações, mas nem todas possuem o mesmo peso estratégico para o sistema. A divisão abaixo ajuda a equipe a concentrar esforços onde as regras são mais importantes.

| Tipo | Subdomínio | Justificativa |
|---|---|---|
| **Core Domain** | Separação e Expedição | É o diferencial operacional: processar grandes volumes, evitar erros de separação e liberar cargas corretamente. |
| **Supportive Domain** | Gestão de Estoque | Dá suporte ao core, controlando lotes, reservas, entradas, saídas e rastreabilidade das movimentações. |
| **Generic Domain** | Gestão de Acessos | Controla usuários, cargos e permissões. É importante, mas pode ser modelado de forma mais simples e mockada. |

### 2.2 Bounded Contexts

Para evitar classes genéricas demais e significados conflitantes, o sistema será dividido em três contextos delimitados.

#### Fulfillment Context — Separação e Expedição

Responsável por:

- pedidos;
- itens;
- separação;
- conferência;
- ordem de expedição;
- liberação da carga.

#### Inventory Context — Estoque

Responsável por:

- lotes;
- reservas;
- movimentações;
- entradas;
- saídas;
- disponibilidade física dos produtos.

#### Identity Context — Usuários e Hierarquia

Responsável por:

- usuários;
- cargos;
- permissões;
- decisões de autorização.

> Essa separação não significa criar sistemas separados. No projeto da disciplina, pode ser apenas uma divisão de pacotes/módulos, mantendo baixo acoplamento entre as partes.

### 2.3 Linguagem Ubíqua

A linguagem ubíqua define os termos que devem aparecer nas conversas, classes, métodos e testes. Isso reduz ambiguidades entre negócio e código.

| Termo | Significado no domínio |
|---|---|
| **Pedido** | Solicitação de um conjunto de bebidas que deve ser separado e expedido. |
| **ItemPedido** | Uma bebida e sua quantidade dentro de um pedido. |
| **Lote de Bebida** | Agrupamento físico de unidades de uma mesma bebida/SKU. |
| **SKU** | Código que identifica uma bebida específica. |
| **Picking / Separação** | Ato de retirar os itens do estoque para atender a um pedido. |
| **Conferência** | Validação de que o pedido separado corresponde ao pedido original. |
| **Ordem de Expedição** | Agrupamento de pedidos que sairão em uma mesma carga. |
| **Movimentação** | Registro imutável de entrada, saída, reserva ou estorno no estoque. |
| **Reserva de Estoque** | Bloqueio temporário de quantidade para atender um pedido. |

---

## 3. DDD Tático e Design Orientado a Objetos

O modelo deve evitar classes anêmicas. As classes principais não devem servir apenas para armazenar dados; elas devem possuir comportamento, validar regras e impedir estados inválidos.

### 3.1 Value Objects

Value Objects não possuem identidade própria e são definidos por seus valores. Devem ser imutáveis sempre que possível.

| Value Object | Regra protegida |
|---|---|
| **Quantidade** | Não pode ser zero ou negativa. |
| **SKU** | Não pode ser vazio e deve seguir um formato definido pela equipe. |
| **TipoBebida** | Restringe os tipos aceitos: Cerveja, Refrigerante e Suco. |
| **CodigoPedido** | Identificador textual válido para pedidos. |
| **CodigoLote** | Identificador textual válido para lotes. |
| **DataExpedicao** | Representa a data planejada de saída da carga. |
| **PrioridadePedido** | Define prioridades simples: Normal, Alta ou Crítica. |

### 3.2 Entidades

Entidades possuem identidade e ciclo de vida. Seus atributos podem mudar, mas sua identidade permanece a mesma.

| Contexto | Entidade | Responsabilidade principal |
|---|---|---|
| **Fulfillment** | Pedido | Controlar o fluxo do pedido e suas transições de estado. |
| **Fulfillment** | ItemPedido | Representar SKU e quantidade solicitada. |
| **Fulfillment** | OrdemExpedicao | Agrupar pedidos separados para uma carga. |
| **Inventory** | LoteBebida | Controlar quantidade disponível, reservada e movimentada. |
| **Inventory** | MovimentacaoEstoque | Registrar eventos de estoque de forma imutável. |
| **Inventory** | ReservaEstoque | Representar uma quantidade reservada para um pedido. |
| **Identity** | Usuario | Representar operador, conferente ou gerente com permissões. |
| **Identity** | Cargo | Definir nível hierárquico e permissões do usuário. |

### 3.3 Aggregates e Aggregate Roots

Agregados protegem consistência. Objetos internos não devem ser alterados livremente por fora; a raiz do agregado concentra as operações permitidas.

#### Agregado Pedido

**Root:** `Pedido`

**Composição:**

- `Pedido` contém uma lista de `ItemPedido`.

**Invariante:**

- O estado do pedido só muda por métodos de negócio, nunca por `setStatus` livre.

**Exemplos de métodos:**

```python
pedido.iniciar_separacao(usuario)
pedido.confirmar_separacao(usuario)
pedido.enviar_para_expedicao(usuario)
pedido.marcar_como_expedido(usuario)
pedido.cancelar(usuario, motivo)
```

#### Agregado EstoqueLote

**Root:** `LoteBebida`

**Composição:**

- lote;
- SKU;
- tipo de bebida;
- quantidade disponível;
- quantidade reservada.

**Invariante:**

- Não pode reservar ou baixar mais itens do que o disponível.

**Exemplos de métodos:**

```python
lote.reservar(quantidade)
lote.confirmar_saida(quantidade)
lote.registrar_entrada(quantidade)
```

#### Agregado OrdemExpedicao

**Root:** `OrdemExpedicao`

**Composição:**

- lista de pedidos já separados e conferidos.

**Invariante:**

- Uma ordem de expedição não pode ser liberada se possuir pedido pendente, em separação ou sem conferência.

### 3.4 Fluxo de Estados do Pedido

O fluxo de estados deve ser simples, mas suficiente para demonstrar regras de negócio.

```text
CRIADO -> AGUARDANDO_ESTOQUE -> EM_SEPARACAO -> SEPARADO -> EM_EXPEDICAO -> EXPEDIDO
   \-> CANCELADO
```

#### Regras principais

- Um pedido criado precisa ter itens válidos.
- Um pedido só entra em separação se houver estoque reservado.
- Um pedido só vira separado depois da confirmação da separação.
- Um pedido só entra em expedição depois de separado e conferido.
- Um pedido expedido não pode ser alterado ou cancelado normalmente.
- O cancelamento exige motivo e permissão adequada.

### 3.5 Hierarquia de Usuários e Permissões

A estrutura de usuário pode ser mockada, sem banco de dados, mas deve existir para permitir decisões de negócio por objeto.

| Cargo | Permissões de negócio |
|---|---|
| **Operador de Estoque** | Registrar entrada de lote, consultar disponibilidade e registrar movimentações simples. |
| **Separador** | Iniciar e finalizar a separação de pedidos. |
| **Conferente** | Conferir pedido separado e aprovar envio para expedição. |
| **Gerente Logístico** | Liberar ordem de expedição, cancelar pedidos de alto volume e autorizar ajustes críticos de estoque. |

### 3.6 Domain Services

Serviços de domínio devem ser usados somente quando uma operação envolve mais de um agregado e não pertence naturalmente a apenas um deles.

Eles **não devem virar serviços gigantes**.

#### Exemplo adequado: `ServicoDeExpedicao`

Responsabilidades:

- verificar se o usuário tem permissão para liberar a expedição;
- verificar se a `OrdemExpedicao` contém apenas pedidos separados e conferidos;
- coordenar a baixa do estoque por meio dos agregados de estoque;
- publicar eventos de domínio, como `PedidoExpedidoEvent` ou `EstoqueBaixadoEvent`.

> Regra de design: o serviço coordena, mas não substitui as regras internas de `Pedido`, `LoteBebida`, `Usuario` ou `OrdemExpedicao`.

### 3.7 Repositories In-Memory

Como não haverá banco de dados, os repositórios serão implementados em memória usando listas ou dicionários.

Mesmo assim, o domínio deve depender de interfaces, não de detalhes de infraestrutura.

| Interface | Implementação em memória |
|---|---|
| `IPedidoRepository` | `PedidoRepositoryInMemory` |
| `IEstoqueRepository` | `EstoqueRepositoryInMemory` |
| `IUsuarioRepository` | `UsuarioRepositoryInMemory` |
| `IOrdemExpedicaoRepository` | `OrdemExpedicaoRepositoryInMemory` |

Isso permite testar as regras do domínio sem depender de banco, API externa ou framework.

---

## 4. Invariantes principais do domínio

Invariantes são regras que o sistema nunca deve permitir quebrar.

- Quantidade de itens, lote ou movimentação nunca pode ser negativa ou zero quando representar entrada/saída real.
- Pedido não pode ser expedido antes de ser separado e conferido.
- Pedido não pode pular estados do fluxo definido.
- Estoque não pode ficar negativo.
- A reserva de estoque não pode exceder a quantidade disponível do lote.
- Somente usuários ativos podem executar ações operacionais.
- Somente o gerente logístico pode liberar ordem de expedição ou cancelar pedido de alto volume.
- Movimentações de estoque devem ser registradas como histórico imutável.
- Ordem de expedição só pode ser liberada se todos os pedidos estiverem separados e conferidos.

---

## 5. Eventos de domínio

Eventos de domínio ajudam a comunicar mudanças importantes sem acoplar diretamente os contextos.

Como não haverá mensageria externa, eles podem ser publicados por um `EventBus` em memória.

### Eventos sugeridos

- `PedidoCriadoEvent`
- `EstoqueReservadoEvent`
- `SeparacaoIniciadaEvent`
- `PedidoSeparadoEvent`
- `PedidoConferidoEvent`
- `OrdemExpedicaoLiberadaEvent`
- `PedidoExpedidoEvent`
- `EstoqueBaixadoEvent`
- `PedidoCanceladoEvent`

Esses eventos não precisam ser complexos. Para o projeto, podem ser classes simples ou dicionários contendo informações como:

- ID do pedido;
- SKU;
- quantidade;
- usuário responsável.

---

## 6. Exemplo anti-anêmico

O modelo não deve permitir alteração livre de status ou quantidade. A regra deve estar dentro do objeto de domínio.

### Exemplo ruim

```python
pedido.status = "EXPEDIDO"
estoque.quantidade = estoque.quantidade - 50000
```

### Exemplo melhor

```python
pedido.marcar_como_expedido(usuario)
lote.confirmar_saida(Quantidade(50000))
```

No segundo exemplo, cada objeto valida sua própria regra:

- `Pedido` valida o fluxo de estados e permissão;
- `LoteBebida` valida a disponibilidade do estoque.

---

## 7. Sugestão de estrutura de pacotes

A estrutura abaixo é simples e suficiente para organizar o projeto sem deixar a arquitetura pesada.

```text
src/
├── fulfillment/
│   ├── domain/
│   │   ├── pedido.py
│   │   ├── item_pedido.py
│   │   ├── ordem_expedicao.py
│   │   └── estado_pedido.py
│   ├── application/
│   │   └── servico_de_expedicao.py
│   └── infrastructure/
│       └── pedido_repository_in_memory.py
│
├── inventory/
│   ├── domain/
│   │   ├── lote_bebida.py
│   │   ├── movimentacao_estoque.py
│   │   └── reserva_estoque.py
│   └── infrastructure/
│       └── estoque_repository_in_memory.py
│
├── identity/
│   ├── domain/
│   │   ├── usuario.py
│   │   └── cargo.py
│   └── infrastructure/
│       └── usuario_repository_in_memory.py
│
└── shared/
    ├── value_objects/
    │   ├── quantidade.py
    │   └── sku.py
    └── events/
        └── event_bus.py
```

---

## 8. Justificativa técnica da linguagem

A linguagem sugerida para implementação é **Python**.

Embora Python seja dinâmico e flexível, é possível aplicar Orientação a Objetos e DDD com disciplina arquitetural.

### Recomendações

- Usar `dataclasses` com `frozen=True` para Value Objects imutáveis.
- Evitar setters livres para estado e quantidade.
- Usar métodos de negócio com nomes claros.
- Separar domínio, aplicação e infraestrutura em módulos simples.
- Testar regras de negócio diretamente nas classes de domínio.
- Usar repositórios in-memory para simular persistência sem banco de dados.

---

## 9. Critérios de sucesso da proposta

A solução será considerada adequada se demonstrar que as regras centrais estão protegidas pelo domínio e não espalhadas em controllers, banco de dados ou scripts soltos.

### O sistema deve demonstrar que:

- o pedido controla seu próprio estado;
- o estoque impede reserva ou baixa inválida;
- usuários e cargos influenciam decisões de negócio;
- serviços coordenam objetos, mas não concentram toda a lógica;
- repositórios em memória permitem testes simples;
- a arquitetura é compreensível e não exageradamente complexa.

---

## 10. Link para visualização em DOCS/PDF mais organizado:

- https://docs.google.com/document/d/1MR8ZlBvmw5I32Q38eGuWazDmu6jLD25kfu97qVfILi0/edit?usp=sharing
