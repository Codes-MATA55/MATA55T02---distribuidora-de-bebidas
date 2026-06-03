package org.br.domain.pedido;

import java.util.List;
import java.util.UUID;

public class Pedido {

    private UUID id;

    private List<ItemPedido> itens;

    private StatusPedido status;

    public Pedido(List<ItemPedido> itens) {
    }


    public UUID getId() {
        return id;
    }

    public void setId(UUID id) {
        this.id = id;
    }

    public List<ItemPedido> getItens() {
        return itens;
    }

    public void setItens(List<ItemPedido> itens) {
        this.itens = itens;
    }

    public StatusPedido getStatus() {
        return status;
    }

    public void setStatus(StatusPedido status) {
        this.status = status;
    }
}