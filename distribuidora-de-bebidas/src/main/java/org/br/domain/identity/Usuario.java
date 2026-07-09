package org.br.domain.identity;

import java.util.UUID;

public class Usuario {

    private final UUID id;
    private final String nome;
    private final Cargo cargo;
    private boolean ativo;

    public Usuario(UUID id, String nome, Cargo cargo, boolean ativo) {

        if (id == null) {
            throw new IllegalArgumentException(
                    "Id do usuário é obrigatório"
            );
        }

        if (nome == null || nome.isBlank()) {
            throw new IllegalArgumentException(
                    "Nome do usuário é obrigatório"
            );
        }

        if (cargo == null) {
            throw new IllegalArgumentException(
                    "Cargo do usuário é obrigatório"
            );
        }

        this.id = id;
        this.nome = nome;
        this.cargo = cargo;
        this.ativo = ativo;
    }

    public boolean pode(Permissao permissao) {
        return ativo && cargo.possui(permissao);
    }

    public UUID getId() {
        return id;
    }

    public String getNome() {
        return nome;
    }

    public Cargo getCargo() {
        return cargo;
    }

    public boolean isAtivo() {
        return ativo;
    }

    public void desativar() {
        this.ativo = false;
    }
}
