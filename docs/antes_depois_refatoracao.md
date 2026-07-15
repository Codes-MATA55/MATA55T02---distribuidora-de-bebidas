# Atividade Formativa 4 : Escrever Antes X Depois das Refatorações

## Objetivo

Registrar refatorações reais guiadas por code smells, preservando comportamento com testes.

---

## Smell 1 — Retorno recursivo em `Product.barcode`

### Antes

A propriedade `barcode` retornava ela mesma:

```python
@property
def barcode(self):
    return self.barcode
```

Problema: isso cria recursão infinita, pois `self.barcode` chama novamente a própria property.

### Depois

A propriedade passou a retornar o atributo interno:

```python
@property
def barcode(self):
    return self._barcode
```

Resultado: o encapsulamento é preservado e o valor correto é retornado.

Arquivo:

```text
src/domain/entities/produto.py
```

---

## Smell 2 — Responsabilidade de JSON espalhada

### Antes

A leitura e escrita de JSON poderiam ficar espalhadas em `main.py`, repositórios ou testes.

Problemas:

- repetição de `open`, `json.load` e `json.dump`;
- maior acoplamento entre fluxo principal e infraestrutura;
- maior chance de regra de negócio ser misturada com persistência simulada.

### Depois

A responsabilidade comum foi centralizada em:

```text
src/domain/json_storage.py
```

Com funções:

```text
read_json(...)
write_json(...)
```

Resultado: repositórios usam JSON sem espalhar detalhes de arquivo pelo domínio.

---

## Smell 3 — Orquestração com risco de virar service gigante

### Antes

O fluxo de criar pedido, separar, expedir e salvar poderia crescer dentro de `main.py`.

Problema: `main.py` poderia virar um script procedural com regras de negócio.

### Depois

A orquestração do caso de uso foi movida para:

```text
src/domain/order_workflow.py
```

`OrderWorkflow` apenas coordena:

```text
confirmar pagamento → separar → expedir → salvar → notificar
```

As decisões continuam nos objetos:

- `Order` decide estados e expedição;
- `StockRegistry` decide baixa de estoque;
- `Batch` decide consumo;
- `TotalSeparation` coordena separação;
- `JsonOrderRepository` salva snapshot.

---

## Smell 4 — Condicional rígida para seleção de lotes

### Antes

A separação poderia ficar presa a uma única ordenação de lotes dentro do método.

Problema: trocar FEFO por outra política exigiria alterar o método de baixa.

### Depois

Foi criada a abstração:

```text
BatchSelectionPolicy
```

Com implementações:

```text
FefoBatchSelectionPolicy
LifoBatchSelectionPolicy
```

Resultado: a variação fica por composição, sem alterar `StockRegistry` ou `TotalSeparation`.

---

## Testes de regressão

Os testes protegem o comportamento após refatoração:

- `test_produto.py`: valida produto e barcode;
- `test_estoque.py`: valida saldo, separação e baixa;
- `test_transicoes_invalidas.py`: valida estados inválidos;
- `test_atividade_avaliativa_1.py`: valida invariantes DDD;
- `test_atividade_avaliativa_2.py`: valida políticas, repositórios e DI.

---

## Conclusão

A refatoração não foi apenas cosmética. Ela removeu recursão, reduziu acoplamento, separou responsabilidades e protegeu o fluxo principal com testes.
