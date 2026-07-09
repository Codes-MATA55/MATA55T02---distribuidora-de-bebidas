package org.br.domain.estoque;

import java.math.BigDecimal;
import java.util.UUID;

public class Produto {

    private UUID id;
    private String nome;
    private TipoProduto tipo;
    private BigDecimal preco;

    public Produto(UUID id, String nome, BigDecimal preco) {
        this(id, nome, null, preco);
    }

    public Produto(UUID id, String nome, TipoProduto tipo, BigDecimal preco) {

        if (id == null) {
            throw new IllegalArgumentException(
                    "Id do produto é obrigatório"
            );
        }

        if (nome == null || nome.isBlank()) {
            throw new IllegalArgumentException(
                    "Nome do produto é obrigatório"
            );
        }

        if (preco == null) {
            throw new IllegalArgumentException(
                    "Preço do produto é obrigatório"
            );
        }

        this.id = id;
        this.nome = nome;
        this.tipo = tipo;
        this.preco = preco;
    }

    public UUID getId() {
        return id;
    }

    public void setId(UUID id) {
        this.id = id;
    }

    public String getNome() {
        return nome;
    }

    public void setNome(String nome) {
        this.nome = nome;
    }

    public TipoProduto getTipo() {
        return tipo;
    }

    public void setTipo(TipoProduto tipo) {
        this.tipo = tipo;
    }

    public BigDecimal getPreco() {
        return preco;
    }

    public void setPreco(BigDecimal preco) {
        this.preco = preco;
    }
}
