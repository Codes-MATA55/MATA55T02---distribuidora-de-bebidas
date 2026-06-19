package org.br.domain.pedido;

import java.util.List;
import java.util.Set;
import java.util.UUID;

/**
 * Entidade de Domínio representando um Pedido.
 * <p>
 * Esta classe atua como uma raiz de agregação (Aggregate Root), encapsulando a 
 * lógica de negócio para transição de status. Ela garante que o pedido sempre 
 * permaneça em um estado válido e consistente do ponto de vista do domínio.
 */
public class Pedido {

    private final UUID id;
    private final List<ItemPedido> itens;
    private StatusPedido status;

    /**
     * Instancia um novo Pedido.
     * * @param itens Lista de itens que compõem o pedido.
     * @throws IllegalArgumentException Se a lista de itens fornecida for nula ou vazia.
     */
    public Pedido(List<ItemPedido> itens) {
        if (itens == null || itens.isEmpty()) {
            throw new IllegalArgumentException("Pedido deve possuir pelo menos um item");
        }

        this.id = UUID.randomUUID();
        // A cópia defensiva garante a imutabilidade da lista de itens após a criação
        this.itens = List.copyOf(itens); 
        this.status = StatusPedido.CRIADO;
    }

    public UUID getId() {
        return id;
    }

    public List<ItemPedido> getItens() {
        return itens;
    }

    public StatusPedido getStatus() {
        return status;
    }

    /**
     * Transita o status do pedido para AGUARDANDO_ESTOQUE.
     * * @throws IllegalStateException Se o pedido não estiver no status CRIADO.
     */
    public void aguardarEstoque() {
        exigirStatus(Set.of(StatusPedido.CRIADO), 
                "Somente pedidos criados podem aguardar estoque");
        
        this.status = StatusPedido.AGUARDANDO_ESTOQUE;
    }

    /**
     * Transita o status do pedido para EM_SEPARACAO.
     * * @throws IllegalStateException Se o pedido não estiver no status CRIADO ou AGUARDANDO_ESTOQUE.
     */
    public void iniciarSeparacao() {
        exigirStatus(Set.of(StatusPedido.CRIADO, StatusPedido.AGUARDANDO_ESTOQUE), 
                "Pedido não pode entrar em separação a partir do status atual");
        
        this.status = StatusPedido.EM_SEPARACAO;
    }

    /**
     * Transita o status do pedido para SEPARADO.
     * * @throws IllegalStateException Se o pedido não estiver EM_SEPARACAO.
     */
    public void separar() {
        exigirStatus(Set.of(StatusPedido.EM_SEPARACAO), 
                "Pedido deve estar em processo de separação para ser concluído");
        
        this.status = StatusPedido.SEPARADO;
    }

    /**
     * Transita o status do pedido para EXPEDIDO.
     * * @throws IllegalStateException Se o pedido não estiver previamente SEPARADO.
     */
    public void expedir() {
        exigirStatus(Set.of(StatusPedido.SEPARADO), 
                "Somente pedidos devidamente separados podem ser expedidos");
        
        this.status = StatusPedido.EXPEDIDO;
    }

    /**
     * Cancela o pedido, impedindo que continue seu fluxo normal.
     * * @throws IllegalStateException Se o pedido já tiver sido EXPEDIDO.
     */
    public void cancelar() {
        proibirStatus(StatusPedido.EXPEDIDO, 
                "Pedido expedido não pode ser cancelado, requer processo de devolução");
        
        this.status = StatusPedido.CANCELADO;
    }

    // --- Métodos Auxiliares de Validação (Guard Clauses) ---
    
    /* * A extração destes métodos consolida a aplicação do padrão Guard Clauses.
     * Essa refatoração previne o aninhamento profundo de blocos "if-else", 
     * falhando rapidamente (fail-fast) e mantendo a qualidade e legibilidade 
     * das regras de transição acima.
     */

    /**
     * Valida se o status atual está presente no conjunto de status permitidos.
     */
    private void exigirStatus(Set<StatusPedido> permitidos, String mensagemErro) {
        if (!permitidos.contains(this.status)) {
            throw new IllegalStateException(mensagemErro);
        }
    }

    /**
     * Valida se o status atual é diferente do status proibido.
     */
    private void proibirStatus(StatusPedido proibido, String mensagemErro) {
        if (this.status == proibido) {
            throw new IllegalStateException(mensagemErro);
        }
    }
}
