package org.br.domain.pedido;

import org.br.domain.estoque.Produto;

import java.util.UUID;

public class ItemPedido {

    private final UUID produtoId;
    private final int quantidade;

    public ItemPedido(UUID produtoId, int quantidade) {

        if (produtoId == null) {
            throw new IllegalArgumentException(
                    "Produto obrigatório"
            );
        }

        if (quantidade <= 0) {
            throw new IllegalArgumentException(
                    "Quantidade deve ser maior que zero"
            );
        }

        this.produtoId = produtoId;
        this.quantidade = quantidade;
    }

    public UUID getProdutoId() {
        return produtoId;
    }

    public int getQuantidade() {
        return quantidade;
    }
}