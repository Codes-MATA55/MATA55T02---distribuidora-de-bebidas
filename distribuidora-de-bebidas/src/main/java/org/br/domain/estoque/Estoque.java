package org.br.domain.estoque;

public class Estoque {

    private Produto produto;
    private int quantidadeDisponivel;

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

    public Produto getProduto() {
        return produto;
    }

    public int getQuantidadeDisponivel() {
        return quantidadeDisponivel;
    }

    public void setProduto(Produto produto) {
        this.produto = produto;
    }

    public void setQuantidadeDisponivel(int quantidadeDisponivel) {
        this.quantidadeDisponivel = quantidadeDisponivel;
    }
}