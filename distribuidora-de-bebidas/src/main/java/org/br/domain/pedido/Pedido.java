package org.br.domain.pedido;

import java.util.List;
import java.util.Set;
import java.util.UUID;

public class Pedido {

    private final UUID id;
    private final List<ItemPedido> itens;
    private StatusPedido status;

    public Pedido(List<ItemPedido> itens) {
        if (itens == null || itens.isEmpty()) {
            throw new IllegalArgumentException("Pedido deve possuir pelo menos um item");
        }

        this.id = UUID.randomUUID();
        this.itens = List.copyOf(itens); // Excelente prática de imutabilidade mantida
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

    public void aguardarEstoque() {
        exigirStatus(Set.of(StatusPedido.CRIADO), 
                "Somente pedidos criados podem aguardar estoque");
        
        this.status = StatusPedido.AGUARDANDO_ESTOQUE;
    }

    public void iniciarSeparacao() {
        exigirStatus(Set.of(StatusPedido.CRIADO, StatusPedido.AGUARDANDO_ESTOQUE), 
                "Pedido não pode entrar em separação");
        
        this.status = StatusPedido.EM_SEPARACAO;
    }

    public void separar() {
        exigirStatus(Set.of(StatusPedido.EM_SEPARACAO), 
                "Pedido deve estar em separação");
        
        this.status = StatusPedido.SEPARADO;
    }

    public void expedir() {
        exigirStatus(Set.of(StatusPedido.SEPARADO), 
                "Somente pedidos separados podem ser expedidos");
        
        this.status = StatusPedido.EXPEDIDO;
    }

    public void cancelar() {
        proibirStatus(StatusPedido.EXPEDIDO, 
                "Pedido expedido não pode ser cancelado");
        
        this.status = StatusPedido.CANCELADO;
    }

    // --- Métodos Auxiliares de Validação (Guard Clauses) ---

    private void exigirStatus(Set<StatusPedido> permitidos, String mensagemErro) {
        if (!permitidos.contains(this.status)) {
            throw new IllegalStateException(mensagemErro);
        }
    }

    private void proibirStatus(StatusPedido proibido, String mensagemErro) {
        if (this.status == proibido) {
            throw new IllegalStateException(mensagemErro);
        }
    }
}
