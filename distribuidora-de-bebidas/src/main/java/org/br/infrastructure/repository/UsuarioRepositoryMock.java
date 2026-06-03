package org.br.infrastructure.repository;

import org.br.domain.usuario.Usuario;
import org.br.domain.usuario.UsuarioRepository;
import org.springframework.stereotype.Repository;

import java.util.*;

@Repository
public class UsuarioRepositoryMock implements UsuarioRepository {

    private final Map<UUID, Usuario> usuarios = new HashMap<>();

    @Override
    public void salvar(Usuario usuario) {
        usuarios.put(
                usuario.getId(),
                usuario
        );
    }

    @Override
    public Optional<Usuario> buscarPorId(UUID id) {
        return Optional.ofNullable(
                usuarios.get(id)
        );
    }

    @Override
    public List<Usuario> listarTodos() {
        return new ArrayList<>(
                usuarios.values()
        );

    }
}
