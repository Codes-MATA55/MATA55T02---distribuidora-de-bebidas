package org.br.domain.estoque;

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

        if (quantidade <= 0) {
            throw new IllegalArgumentException(
                    "Quantidade deve ser maior que zero"
            );
        }

        if (quantidadeDisponivel < quantidade) {
            throw new IllegalArgumentException(
                    "Estoque insuficiente para o produto "
                            + produto.getNome()
            );
        }

        quantidadeDisponivel -= quantidade;
    }

    public void adicionar(int quantidade) {

        if (quantidade <= 0) {
            throw new IllegalArgumentException(
                    "Quantidade deve ser maior que zero"
            );
        }

        quantidadeDisponivel += quantidade;
    }

    public Produto getProduto() {
        return produto;
    }

    public int getQuantidadeDisponivel() {
        return quantidadeDisponivel;
    }
}