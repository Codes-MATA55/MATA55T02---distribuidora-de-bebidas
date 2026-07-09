package domain.expedicao;

import org.br.domain.expedicao.OrdemExpedicao;
import org.br.domain.identity.Cargo;
import org.br.domain.identity.Usuario;
import org.br.domain.pedido.Pedido;
import org.br.domain.pedido.StatusPedido;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import java.util.List;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

class OrdemExpedicaoTest {

    @Test
    @DisplayName("Gerente deve liberar ordem com pedido separado")
    void gerenteDeveLiberarOrdemComPedidoSeparado() {

        Pedido pedido = mock(Pedido.class);

        when(pedido.getStatus())
                .thenReturn(StatusPedido.SEPARADO);

        Usuario gerente = new Usuario(
                UUID.randomUUID(),
                "Gerente",
                Cargo.GERENTE_LOGISTICO,
                true
        );

        OrdemExpedicao ordem = new OrdemExpedicao(List.of(pedido));

        ordem.liberar(gerente);

        assertTrue(ordem.isLiberada());
    }

    @Test
    @DisplayName("Nao deve liberar ordem com usuario sem permissao")
    void naoDeveLiberarOrdemComUsuarioSemPermissao() {

        Pedido pedido = mock(Pedido.class);

        Usuario separador = new Usuario(
                UUID.randomUUID(),
                "Separador",
                Cargo.SEPARADOR,
                true
        );

        OrdemExpedicao ordem = new OrdemExpedicao(List.of(pedido));

        assertThrows(
                IllegalStateException.class,
                () -> ordem.liberar(separador)
        );
    }

    @Test
    @DisplayName("Nao deve liberar ordem com pedido ainda criado")
    void naoDeveLiberarOrdemComPedidoAindaCriado() {

        Pedido pedido = mock(Pedido.class);

        when(pedido.getStatus())
                .thenReturn(StatusPedido.CRIADO);

        Usuario gerente = new Usuario(
                UUID.randomUUID(),
                "Gerente",
                Cargo.GERENTE_LOGISTICO,
                true
        );

        OrdemExpedicao ordem = new OrdemExpedicao(List.of(pedido));

        assertThrows(
                IllegalStateException.class,
                () -> ordem.liberar(gerente)
        );
    }
}
