package org.br.domain.pedido;

import java.util.List;
import java.util.UUID;

public class Pedido {

    private final UUID id;
    private final List<ItemPedido> itens;
    private StatusPedido status;

    public Pedido(List<ItemPedido> itens) {

        if (itens == null || itens.isEmpty()) {
            throw new IllegalArgumentException(
                    "Pedido deve possuir pelo menos um item"
            );
        }

        this.id = UUID.randomUUID();
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

    public void aguardarEstoque() {

        if (status != StatusPedido.CRIADO) {
            throw new IllegalStateException(
                    "Somente pedidos criados podem aguardar estoque"
            );
        }

        this.status = StatusPedido.AGUARDANDO_ESTOQUE;
    }

    public void iniciarSeparacao() {

        if (status != StatusPedido.CRIADO &&
                status != StatusPedido.AGUARDANDO_ESTOQUE) {

            throw new IllegalStateException(
                    "Pedido não pode entrar em separação"
            );
        }

        this.status = StatusPedido.EM_SEPARACAO;
    }

    public void separar() {

        if (status != StatusPedido.EM_SEPARACAO) {
            throw new IllegalStateException(
                    "Pedido deve estar em separação"
            );
        }

        this.status = StatusPedido.SEPARADO;
    }

    public void expedir() {

        if (status != StatusPedido.SEPARADO) {
            throw new IllegalStateException(
                    "Somente pedidos separados podem ser expedidos"
            );
        }

        this.status = StatusPedido.EXPEDIDO;
    }

    public void cancelar() {

        if (status == StatusPedido.EXPEDIDO) {
            throw new IllegalStateException(
                    "Pedido expedido não pode ser cancelado"
            );
        }

        this.status = StatusPedido.CANCELADO;
    }
}