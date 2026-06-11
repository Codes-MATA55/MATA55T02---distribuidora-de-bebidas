package org.br.domain.shared;

import java.util.Objects;

public class Quantidade {

    private final Integer valor;

    public Quantidade(Integer valor) {

        if (valor == null) {
            throw new DomainException(
                    "Quantidade não pode ser nula"
            );
        }

        if (valor <= 0) {
            throw new DomainException(
                    "Quantidade deve ser maior que zero"
            );
        }

        this.valor = valor;
    }

    public Integer getValor() {
        return valor;
    }

    public Quantidade adicionar(Quantidade outra) {
        return new Quantidade(
                this.valor + outra.valor
        );
    }

    public Quantidade subtrair(Quantidade outra) {

        if (this.valor < outra.valor) {
            throw new DomainException(
                    "Quantidade insuficiente"
            );
        }

        return new Quantidade(
                this.valor - outra.valor
        );
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof Quantidade)) return false;
        Quantidade that = (Quantidade) o;
        return Objects.equals(valor, that.valor);
    }

    @Override
    public int hashCode() {
        return Objects.hash(valor);
    }

    @Override
    public String toString() {
        return String.valueOf(valor);
    }
}
