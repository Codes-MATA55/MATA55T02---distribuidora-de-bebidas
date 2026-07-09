package org.br.domain.pedido;

import org.br.shared.valueobject.Quantidade;

import java.util.UUID;

public class ItemPedido {

    private final UUID produtoId;
    private final Quantidade quantidade;

    public ItemPedido(UUID produtoId, int quantidade) {
        this(produtoId, new Quantidade(quantidade));
    }

    public ItemPedido(UUID produtoId, Quantidade quantidade) {

        if (produtoId == null) {
            throw new IllegalArgumentException(
                    "Produto obrigatório"
            );
        }

        if (quantidade == null) {
            throw new IllegalArgumentException(
                    "Quantidade obrigatória"
            );
        }

        this.produtoId = produtoId;
        this.quantidade = quantidade;
    }

    public UUID getProdutoId() {
        return produtoId;
    }

    public int getQuantidade() {
        return quantidade.valor();
    }

    public Quantidade getQuantidadeValueObject() {
        return quantidade;
    }
}
