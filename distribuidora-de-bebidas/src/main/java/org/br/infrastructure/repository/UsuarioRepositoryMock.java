package org.br.infrastructure.repository;

import org.br.domain.identity.Cargo;
import org.br.domain.identity.Usuario;
import org.br.domain.identity.UsuarioRepository;
import org.springframework.stereotype.Repository;

import java.util.HashMap;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;

@Repository
public class UsuarioRepositoryMock implements UsuarioRepository {

    private final Map<UUID, Usuario> usuarios = new HashMap<>();

    public UsuarioRepositoryMock() {
        salvar(
                new Usuario(
                        UUID.randomUUID(),
                        "Operador de Estoque",
                        Cargo.OPERADOR_ESTOQUE,
                        true
                )
        );

        salvar(
                new Usuario(
                        UUID.randomUUID(),
                        "Gerente Logístico",
                        Cargo.GERENTE_LOGISTICO,
                        true
                )
        );
    }

    @Override
    public void salvar(Usuario usuario) {
        usuarios.put(usuario.getId(), usuario);
    }

    @Override
    public Optional<Usuario> buscarPorId(UUID id) {
        return Optional.ofNullable(usuarios.get(id));
    }
}
