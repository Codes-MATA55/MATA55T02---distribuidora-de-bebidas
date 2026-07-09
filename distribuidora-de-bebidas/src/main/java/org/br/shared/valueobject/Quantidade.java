package org.br.shared.valueobject;

public record Quantidade(int valor) {

    public Quantidade {
        if (valor <= 0) {
            throw new IllegalArgumentException(
                    "Quantidade deve ser maior que zero"
            );
        }
    }
}
