package org.br.domain.pedido;

import org.br.domain.estoque.Produto;

import java.util.UUID;

public class ItemPedido {

    private Produto produto;

    private int quantidade;

    public ItemPedido(UUID produtoId, Integer quantidade) {
    }

    public Produto getProduto() {
        return produto;
    }

    public void setProduto(Produto produto) {
        this.produto = produto;
    }

    public int getQuantidade() {
        return quantidade;
    }

    public void setQuantidade(int quantidade) {
        this.quantidade = quantidade;
    }
}
