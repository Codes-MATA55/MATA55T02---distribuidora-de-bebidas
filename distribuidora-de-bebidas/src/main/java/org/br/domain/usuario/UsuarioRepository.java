package org.br.domain.usuario;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

public interface UsuarioRepository {

    void salvar(Usuario usuario);

    Optional<Usuario> buscarPorId(UUID id);

    List<Usuario> listarTodos();

}
