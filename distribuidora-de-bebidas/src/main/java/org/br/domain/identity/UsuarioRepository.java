package org.br.domain.identity;

import java.util.Optional;
import java.util.UUID;

public interface UsuarioRepository {

    void salvar(Usuario usuario);

    Optional<Usuario> buscarPorId(UUID id);
}
