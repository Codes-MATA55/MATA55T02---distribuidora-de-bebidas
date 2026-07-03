package org.br.shared.value_objects;

import java.util.Objects;

public class Quantidade {
    private final int valor;

    public Quantidade(int valor) {
        if (valor <= 0) {
            throw new IllegalArgumentException("Quantidade deve ser maior que zero");
        }
        this.valor = valor;
    }

    public int getValor() {
        return valor;
    }

    public Quantidade subtrair(Quantidade outra) {
        int resultado = this.valor - outra.valor;
        if (resultado < 0) {
            throw new IllegalArgumentException("Quantidade não pode ser negativa");
        }
        return new Quantidade(resultado);
    }

    public Quantidade somar(Quantidade outra) {
        return new Quantidade(this.valor + outra.valor);
    }

    public boolean isMenorQue(Quantidade outra) {
        return this.valor < outra.valor;
    }

    public boolean isMaiorQue(Quantidade outra) {
        return this.valor > outra.valor;
    }

    @Override
    public boolean equals(Object o) {
        if (this == o) return true;
        if (o == null || getClass() != o.getClass()) return false;
        Quantidade that = (Quantidade) o;
        return valor == that.valor;
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
