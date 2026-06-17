# Distribuidora de Bebidas

Projeto academico da disciplina de Orientacao a Objetos para modelar o dominio de uma distribuidora de bebidas em alta escala.

Autor: Renato Marcelo

## Objetivo

O objetivo do projeto nao e construir um CRUD de bebidas. O foco e aplicar Orientacao a Objetos para modelagem, design, manutencao, evolucao, testabilidade e protecao de regras de negocio.

O sistema trabalha com conceitos do dominio como:

- pedidos;
- estoque;
- separacao;
- expedicao;
- estados do pedido;
- regras de negocio;
- colaboracao entre objetos;
- repositories mockados, sem banco de dados.

## Requisitos do Projeto

De acordo com as regras do professor, o projeto deve demonstrar:

- objetos de dominio com comportamento, evitando modelo anemico;
- protecao das transicoes de estado do pedido;
- estoque tratado como objeto de dominio, nao apenas como numero solto;
- expedicao bloqueada quando as regras do dominio nao permitirem;
- services sem concentrar toda a inteligencia do sistema;
- testes de comportamento, nao apenas testes para aumentar cobertura;
- decisoes de DDD Estrategico e DDD Tatico justificaveis;
- separacao entre dominio, aplicacao, API e infraestrutura.

## Squad Refatoracao

A Squad Refatoracao e responsavel por apoiar a proposta de DDD Estrategico e DDD Tatico da distribuidora.

Pontos analisados pela squad:

- subdominios;
- bounded contexts;
- linguagem ubiqua;
- entidades;
- value objects;
- aggregates;
- domain services;
- repositories;
- invariantes principais.

## Tecnologias

- Java 21
- Spring Boot 3.5.3
- Maven
- JUnit 5
- Mockito

## Estrutura do Projeto

```text
src/main/java/org/br
|-- api              # Controllers REST
|-- application      # Use cases, DTOs e mappers
|-- domain           # Entidades, regras e contratos de repositorio
|-- infrastructure   # Implementacoes mockadas dos repositories
```

## Como Subir o Projeto

Antes de rodar, confirme que o Java 21 e o Maven estao instalados:

```bash
java -version
mvn -version
```

Para iniciar a aplicacao:

```bash
mvn spring-boot:run
```

Por padrao, a API sobe em:

```text
http://localhost:8080
```

## Endpoints Principais

```http
POST /pedidos
GET /pedidos/{id}
POST /pedidos/{id}/reservar
POST /pedidos/{id}/separar
POST /pedidos/{id}/expedir
```

## Como Rodar os Testes

Para executar todos os testes:

```bash
mvn test
```

Para executar uma classe de teste especifica:

```bash
mvn -Dtest=PedidoTest test
```

Exemplos de testes importantes:

- `PedidoTest`: valida estados e transicoes do pedido;
- `EstoqueTest`: valida reserva, adicao e estoque insuficiente;
- `ExpedicaoTest`: valida registro de expedicao apenas quando permitido;
- `ReservarEstoqueUseCaseTest`: valida a colaboracao entre pedido e estoque;
- `ExpedirPedidoUseCaseTest`: valida a expedicao e o registro da expedicao.

## Regras de Dominio

### Pedido

Um pedido nao deve mudar de estado livremente. As mudancas passam por metodos de dominio:

- `aguardarEstoque()`
- `iniciarSeparacao()`
- `separar()`
- `expedir()`
- `cancelar()`

### Estoque

O estoque protege suas proprias regras:

- nao aceita produto nulo;
- nao aceita quantidade inicial negativa;
- nao permite reservar quantidade menor ou igual a zero;
- nao permite reservar mais do que a quantidade disponivel.

### Expedicao

A expedicao representa o registro da operacao logistica. Ela so pode ser registrada quando o pedido ja foi expedido, garantindo que a regra do dominio seja respeitada.

## Observacao Sobre Banco de Dados

O projeto nao usa banco de dados. Os repositories em `infrastructure` sao implementacoes mockadas/em memoria, conforme permitido pelo enunciado.