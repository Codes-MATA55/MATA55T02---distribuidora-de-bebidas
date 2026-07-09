package org.br.domain.estoque;

import org.br.shared.valueobject.Quantidade;

public class Estoque {

    private final Produto produto;
    private int quantidadeDisponivel;

    public Estoque(Produto produto, int quantidadeDisponivel) {

        if (produto == null) {
            throw new IllegalArgumentException(
                    "Produto é obrigatório"
            );
        }

        if (quantidadeDisponivel < 0) {
            throw new IllegalArgumentException(
                    "Quantidade disponível não pode ser negativa"
            );
        }

        this.produto = produto;
        this.quantidadeDisponivel = quantidadeDisponivel;
    }

    public void reservar(int quantidade) {
        reservar(new Quantidade(quantidade));
    }

    public void reservar(Quantidade quantidade) {

        if (quantidade == null) {
            throw new IllegalArgumentException(
                    "Quantidade obrigatória"
            );
        }

        if (quantidadeDisponivel < quantidade.valor()) {
            throw new IllegalArgumentException(
                    "Estoque insuficiente para o produto "
                            + produto.getNome()
            );
        }

        quantidadeDisponivel -= quantidade.valor();
    }

    public void adicionar(int quantidade) {
        adicionar(new Quantidade(quantidade));
    }

    public void adicionar(Quantidade quantidade) {

        if (quantidade == null) {
            throw new IllegalArgumentException(
                    "Quantidade obrigatória"
            );
        }

        quantidadeDisponivel += quantidade.valor();
    }

    public Produto getProduto() {
        return produto;
    }

    public int getQuantidadeDisponivel() {
        return quantidadeDisponivel;
    }
}
