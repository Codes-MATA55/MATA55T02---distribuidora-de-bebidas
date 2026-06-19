package org.br.domain.estoque;

public class Estoque {

    private static final String MSG_PRODUTO_OBRIGATORIO = "Produto é obrigatório";
    private static final String MSG_QTD_NEGATIVA = "Quantidade disponível não pode ser negativa";
    private static final String MSG_QTD_MAIOR_ZERO = "Quantidade deve ser maior que zero";

    private final Produto produto;
    private int quantidadeDisponivel;

    public Estoque(Produto produto, int quantidadeDisponivel) {
        if (produto == null) {
            throw new IllegalArgumentException(MSG_PRODUTO_OBRIGATORIO);
        }
        if (quantidadeDisponivel < 0) {
            throw new IllegalArgumentException(MSG_QTD_NEGATIVA);
        }

        this.produto = produto;
        this.quantidadeDisponivel = quantidadeDisponivel;
    }

    public void reservar(int quantidade) {
        validarQuantidadePositiva(quantidade);

        if (quantidadeDisponivel < quantidade) {
            // Refatoração ideal: utilizar uma Domain Exception personalizada
            // throw new EstoqueInsuficienteException(produto, quantidade);
            throw new IllegalArgumentException(
                    "Estoque insuficiente para o produto " + produto.getNome()
            );
        }

        this.quantidadeDisponivel -= quantidade;
    }

    public void adicionar(int quantidade) {
        validarQuantidadePositiva(quantidade);
        this.quantidadeDisponivel += quantidade;
    }

    private void validarQuantidadePositiva(int quantidade) {
        if (quantidade <= 0) {
            throw new IllegalArgumentException(MSG_QTD_MAIOR_ZERO);
        }
    }

    public Produto getProduto() {
        return produto;
    }

    public int getQuantidadeDisponivel() {
        return quantidadeDisponivel;
    }
}
