package domain.identity;

import org.br.domain.identity.Cargo;
import org.br.domain.identity.Permissao;
import org.br.domain.identity.Usuario;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import java.util.UUID;

import static org.junit.jupiter.api.Assertions.assertFalse;
import static org.junit.jupiter.api.Assertions.assertTrue;

class UsuarioTest {

    @Test
    @DisplayName("Gerente logistico deve poder liberar expedicao")
    void gerenteLogisticoDevePoderLiberarExpedicao() {

        Usuario usuario = new Usuario(
                UUID.randomUUID(),
                "Gerente",
                Cargo.GERENTE_LOGISTICO,
                true
        );

        assertTrue(usuario.pode(Permissao.LIBERAR_EXPEDICAO));
    }

    @Test
    @DisplayName("Usuario inativo nao deve executar permissao do cargo")
    void usuarioInativoNaoDeveExecutarPermissaoDoCargo() {

        Usuario usuario = new Usuario(
                UUID.randomUUID(),
                "Separador",
                Cargo.SEPARADOR,
                false
        );

        assertFalse(usuario.pode(Permissao.SEPARAR_PEDIDO));
    }
}
