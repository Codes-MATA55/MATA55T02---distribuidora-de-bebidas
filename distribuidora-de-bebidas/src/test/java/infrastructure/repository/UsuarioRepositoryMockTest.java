package infrastructure.repository;

import org.br.domain.identity.Cargo;
import org.br.domain.identity.Usuario;
import org.br.infrastructure.repository.UsuarioRepositoryMock;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import java.util.UUID;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertTrue;

class UsuarioRepositoryMockTest {

    @Test
    @DisplayName("Deve salvar e buscar usuario em memoria")
    void deveSalvarEBuscarUsuarioEmMemoria() {

        UsuarioRepositoryMock repository = new UsuarioRepositoryMock();
        Usuario usuario = new Usuario(
                UUID.randomUUID(),
                "Conferente",
                Cargo.CONFERENTE,
                true
        );

        repository.salvar(usuario);

        assertTrue(repository.buscarPorId(usuario.getId()).isPresent());
        assertEquals(
                usuario,
                repository.buscarPorId(usuario.getId()).orElseThrow()
        );
    }
}
