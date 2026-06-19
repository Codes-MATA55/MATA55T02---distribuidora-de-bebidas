package org.br.domain.estoque;

/**
 * Representa o estoque físico ou lógico de um {@link Produto}.
 * <p>
 * Esta classe de domínio centraliza as regras de negócio associadas à entrada e 
 * saída de itens, garantindo que as quantidades disponíveis nunca fiquem negativas 
 * ou inconsistentes.
 * </p>
 */
public class Estoque {

    private static final String MSG_PRODUTO_OBRIGATORIO = "Produto é obrigatório";
    private static final String MSG_QTD_NEGATIVA = "Quantidade disponível não pode ser negativa";
    private static final String MSG_QTD_MAIOR_ZERO = "Quantidade deve ser maior que zero";

    private final Produto produto;
    private int quantidadeDisponivel;

    /**
     * Cria uma nova instância de Estoque para o produto especificado.
     *
     * @param produto              O produto a ser gerido no estoque. Não pode ser nulo.
     * @param quantidadeDisponivel A quantidade inicial disponível. Não pode ser negativa.
     * @throws IllegalArgumentException Se o produto for nulo ou a quantidade inicial for menor que zero.
     */
    public Estoque(final Produto produto, final int quantidadeDisponivel) {
        if (produto == null) {
            throw new IllegalArgumentException(MSG_PRODUTO_OBRIGATORIO);
        }
        
        if (quantidadeDisponivel < 0) {
            throw new IllegalArgumentException(MSG_QTD_NEGATIVA);
        }

        this.produto = produto;
        this.quantidadeDisponivel = quantidadeDisponivel;
    }

    /**
     * Reserva uma quantidade específica do produto no estoque, deduzindo-a da disponibilidade atual.
     * <p>
     * TODO: Refatorar o lançamento da exceção genérica (IllegalArgumentException) 
     * para uma Domain Exception personalizada, como EstoqueInsuficienteException.
     * </p>
     *
     * @param quantidade A quantidade a ser reservada. Deve ser estritamente maior que zero.
     * @throws IllegalArgumentException Se a quantidade solicitada for menor ou igual a zero,
     * ou se for maior que a quantidade atualmente disponível.
     */
    public void reservar(final int quantidade) {
        validarQuantidadePositiva(quantidade);

        if (quantidadeDisponivel < quantidade) {
            throw new IllegalArgumentException(
                String.format("Estoque insuficiente para o produto %s", produto.getNome())
            );
        }

        this.quantidadeDisponivel -= quantidade;
    }

    /**
     * Adiciona uma nova quantidade do produto ao estoque disponível.
     *
     * @param quantidade A quantidade a ser adicionada. Deve ser estritamente maior que zero.
     * @throws IllegalArgumentException Se a quantidade fornecida for menor ou igual a zero.
     */
    public void adicionar(final int quantidade) {
        validarQuantidadePositiva(quantidade);
        
        this.quantidadeDisponivel += quantidade;
    }

    /**
     * Valida se a quantidade informada para operações de estoque é estritamente positiva.
     *
     * @param quantidade O valor da quantidade a ser validada.
     * @throws IllegalArgumentException Se a quantidade for menor ou igual a zero.
     */
    private void validarQuantidadePositiva(final int quantidade) {
        if (quantidade <= 0) {
            throw new IllegalArgumentException(MSG_QTD_MAIOR_ZERO);
        }
    }

    /**
     * Recupera o produto associado a este estoque.
     *
     * @return A instância de {@link Produto} gerenciada.
     */
    public Produto getProduto() {
        return produto;
    }

    /**
     * Recupera a quantidade atualmente disponível para reserva no estoque.
     *
     * @return Um número inteiro representando os itens disponíveis.
     */
    public int getQuantidadeDisponivel() {
        return quantidadeDisponivel;
    }
}
