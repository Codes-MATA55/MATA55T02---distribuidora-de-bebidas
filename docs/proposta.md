[Proposta Inicial - Squad ModelagemProfunda.md](https://github.com/user-attachments/files/28576050/Proposta.Inicial.-.Squad.ModelagemProfunda.md)
# **Sistema de Distribuição de Bebidas em Alta Escala**

**Squad** Modelagem Profunda

Instituto de Computação \- Universidade Federal da Bahia (UFBA)

## **1\. Entendimento do Domínio da Distribuidora**

O projeto consiste no desenvolvimento de um sistema robusto orientado a objetos focado na gestão operacional de uma Distribuidora de Bebidas em Alta Escala. O domínio é caracterizado por um volume massivo de transações e movimentações diárias:

* **Cervejas:** 50.000 unidades por dia.  
* **Refrigerantes:** 30.000 unidades por dia.  
* **Sucos:** 100.000 unidades por dia.

O escopo do sistema abrange o gerenciamento de fluxos críticos como a criação de pedidos, controle dinâmico de estoque, processos de separação (picking) e expedição (dispatch). O principal diferencial arquitetural deste projeto é a rejeição completa a soluções baseadas em CRUDs simplistas ou modelos anêmicos. O foco absoluto está na proteção das regras de negócio diretamente nas classes de domínio por meio do comportamento dos objetos, garantindo alta testabilidade, manutenibilidade e flexibilidade para evoluções futuras.

## **2\. Diretrizes Organizacionais e Escopo da Squad**

A Squad Modelagem Profunda é totalmente responsável por conceber, codificar e evoluir o seu próprio sistema de bebidas individualmente, sem compartilhamento ou dependência de base de código com outras equipes. Nosso foco analítico está na aplicação estratégica de Padrões de Projeto (Design Patterns) para mitigar o acoplamento estrutural, prever pontos de variação e isolar o núcleo do negócio de complexidades desnecessárias.

## **3\. Proposta de Padrões de Projeto (Design Patterns)**

A espinha dorsal da nossa modelagem profunda reside na identificação precisa de onde o domínio tende a variar e quais soluções estruturadas e consolidadas da indústria podem nos apoiar sem gerar overengineering.

| Ponto de Variação do Domínio | Padrão de Projeto Sugerido | Justificativa e Proteção do Design   |
| :---- | :---- | :---- |
| Transições e regras de status dos Pedidos (Aberto, Separação, Expedido, Cancelado). | **State Pattern** | Evita a alteração livre de status e condicionais complexas espalhadas no código. Cada estado encapsula suas próprias regras de transição válidas. |
| Políticas de prioridade de picking, cálculo de frete ou taxas específicas por tipo de bebida. | **Strategy Pattern** | Isola algoritmos variantes do fluxo principal. Permite adicionar novas regras fiscais ou logísticas sem modificar a classe de negócio principal (respeitando o Open/Closed Principle). |
| Instanciação segura de agregados complexos e validação de invariantes na criação de lotes de bebidas. | **Factory Method / Builder** | Garante o acoplamento abstrato e encapsula a complexidade de criação, assegurando que nenhum objeto de domínio nasça em estado inválido. |

### **Prevenção de Overengineering e Padrões Rejeitados**

Seguindo as premissas de um design limpo, determinamos que certos padrões não devem ser aplicados nesta fase inicial para evitar complexidade desnecessária:

* **Mediator:** Rejeitado inicialmente, pois a comunicação direta e bem definida entre os agregados (como Pedido e Estoque) ainda não apresenta um emaranhado complexo de conexões que justifique um objeto mediador centralizado.  
* **Visitor:** Rejeitado devido à estabilidade na estrutura de classes de bebidas. O Visitor adicionaria uma complexidade de duplo despacho desnecessária para um sistema que não precisa estender comportamentos externos em classes de terceiros fechadas.

## **4\. Hipóteses de DDD Estratégico e Tático**

Para organizar adequadamente o nosso próprio ecossistema de software, mapeamos as fronteiras conceituais do negócio:

### **DDD Estratégico**

* **Core Domain (Domínio Central):** Contexto de Pedidos e Expedição. Onde reside o valor competitivo da alta escala e o controle estrito dos estados operacionais.  
* **Supporting Domain (Domínio de Suporte):** Contexto de Controle de Estoque e Separação (Picking). Essencial para apoiar a execução do Core Domain.  
* **Generic Domain (Domínio Genérico):** Gestão cadastral de usuários e divisões hierárquicas. Esta camada será totalmente simulada (Mockada), sem uso de persistência real ou banco de dados.

### **DDD Tático**

* **Aggregates (Agregados):** O objeto Pedido atuará como uma raiz de agregado, encapsulando seus respectivos itens e protegendo as invariantes de negócio de forma isolada.  
* **Entities (Entidades):** Objetos com identidade contínua no tempo, como Pedido e LoteEstoque.  
* **Value Objects (Objetos de Valor):** Conceitos imutáveis definidos apenas por seus atributos, tais como StatusPedido, SKU, Quantidade e DadosUsuario.

## **5\. Hipóteses de Classes e Comportamentos (Código Rico)**

Abaixo é apresentada uma demonstração conceitual da nossa modelagem tática com foco em comportamento rico, eliminando qualquer risco de modelo anêmico. O exemplo ilustra a proteção de estados utilizando o State Pattern estruturado em Python:

from abc import ABC, abstractmethod

class EstadoPedido(ABC):  
    @abstractmethod  
    def avancar(self, pedido):  
        pass

    @abstractmethod  
    def cancelar(self, pedido):  
        pass

class EstadoAberto(EstadoPedido):  
    def avancar(self, pedido):  
        \# Valida regras de negócio de estoque antes de alterar status  
        pedido.definir\_estado(EstadoEmSeparacao())  
      
    def cancelar(self, pedido):  
        pedido.definir\_estado(EstadoCancelado())

class EstadoEmSeparacao(EstadoPedido):  
    def avancar(self, pedido):  
        \# Invariante: Só avança se a separação física do lote foi concluída  
        pedido.definir\_estado(EstadoExpedido())  
      
    def cancelar(self, pedido):  
        raise RuntimeError("Não é possível cancelar um pedido já em fase de separação física.")

class Pedido:  
    def \_\_init\_\_(self, id\_pedido: str):  
        self.id \= id\_pedido  
        self.\_estado: EstadoPedido \= EstadoAberto()  
        self.itens \= \[\]

    def definir\_estado(self, novo\_estado: EstadoPedido):  
        self.\_estado \= novo\_estado

    def avancar\_fluxo(self):  
        self.\_estado.avancar(self)

    def solicitar\_cancelamento(self):  
        self.\_estado.cancelar(self)

## **6\. Proposta de Camadas e Fronteiras**

Para blindar o negócio e garantir o desacoplamento arquitetural, o sistema adotará uma separação em camadas rígidas:

1. **Camada de Domínio (Domain):** Contém as Entidades, Value Objects, Interfaces de Repositories e as regras fundamentais. Esta camada é pura, sem referências a frameworks, bibliotecas externas ou mecanismos de infraestrutura.  
2. **Camada de Aplicação (Application):** Orquestra os fluxos de caso de uso (ex: ProcessarNovoPedidoUseCase). Ela recupera os agregados através das interfaces e aciona seus comportamentos. Não contém lógica de decisão de negócio.  
3. **Camada de Infraestrutura (Infrastructure):** Responsável pelas implementações concretas de entrada e saída. Como não utilizaremos banco de dados, aqui ficarão os repositórios em memória baseados em coleções nativas e as simulações (Mocks) dos dados cadastrais de usuários.

## **7\. Riscos Técnicos e Mitigação de Code Smells**

Mapeamos os principais gargalos que tendem a degradar a qualidade do código com o avanço do calendário acadêmico:

* **Primitive Obsession (Obsessão por Primitivos):** Tratar o saldo do estoque ou o identificador SKU como simples inteiros ou strings soltas. Mitigação: Criação de pequenos Objetos de Valor com regras auto-validadoras no construtor.  
* **Large Class / Service Gigante:** Concentrar toda a inteligência de alocação de bebidas em classes de serviço orquestradoras. Mitigação: Transferir a responsabilidade lógica de dedução diretamente para o método interno do agregado de Estoque.  
* **Alteração Livre de Status:** Expor mutadores públicos que permitam burlar as regras de transição. Mitigação: Encapsulamento estrito do estado interno protegendo as operações através do padrão State.

## **8\. Plano Inicial de Testes Automatizados**

Os testes não serão aplicados como métrica vazia de cobertura, mas sim como proteção ativa para refatorações contínuas. O foco inicial será estruturado em:

* **Testes Unitários de Comportamento:** Validar se um pedido impede a sua própria expedição caso o estoque correspondente não tenha sido previamente separado.  
* **Testes de Invariantes de Estado:** Assegurar que disparos inválidos de transições (ex: cancelar um pedido já em fase de separação física) lancem exceções controladas de domínio.
