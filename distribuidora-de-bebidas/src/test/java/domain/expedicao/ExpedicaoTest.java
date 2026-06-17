package domain.expedicao;

import org.br.domain.expedicao.Expedicao;
import org.br.domain.pedido.ItemPedido;
import org.br.domain.pedido.Pedido;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.*;

class ExpedicaoTest {

    @Test
    @DisplayName("Deve registrar expedicao para pedido expedido")
    void deveRegistrarExpedicaoParaPedidoExpedido() {

        Pedido pedido = criarPedidoExpedido();

        LocalDateTime antesDaExpedicao = LocalDateTime.now();

        Expedicao expedicao = new Expedicao(pedido);

        LocalDateTime depoisDaExpedicao = LocalDateTime.now();

        assertNotNull(expedicao.getId());
        assertEquals(pedido.getId(), expedicao.getPedidoId());
        assertNotNull(expedicao.getDataExpedicao());
        assertFalse(expedicao.getDataExpedicao().isBefore(antesDaExpedicao));
        assertFalse(expedicao.getDataExpedicao().isAfter(depoisDaExpedicao));
    }

    @Test
    @DisplayName("Nao deve registrar expedicao sem pedido")
    void naoDeveRegistrarExpedicaoSemPedido() {

        IllegalArgumentException exception =
                assertThrows(
                        IllegalArgumentException.class,
                        () -> new Expedicao(null)
                );

        assertEquals(
                "Pedido é obrigatório",
                exception.getMessage()
        );
    }

    @Test
    @DisplayName("Nao deve registrar expedicao para pedido criado")
    void naoDeveRegistrarExpedicaoParaPedidoCriado() {

        Pedido pedido = criarPedido();

        IllegalStateException exception =
                assertThrows(
                        IllegalStateException.class,
                        () -> new Expedicao(pedido)
                );

        assertEquals(
                "Expedição só pode ser registrada para pedido expedido",
                exception.getMessage()
        );
    }

    @Test
    @DisplayName("Nao deve registrar expedicao para pedido em separacao")
    void naoDeveRegistrarExpedicaoParaPedidoEmSeparacao() {

        Pedido pedido = criarPedido();
        pedido.iniciarSeparacao();

        IllegalStateException exception =
                assertThrows(
                        IllegalStateException.class,
                        () -> new Expedicao(pedido)
                );

        assertEquals(
                "Expedição só pode ser registrada para pedido expedido",
                exception.getMessage()
        );
    }

    @Test
    @DisplayName("Nao deve registrar expedicao para pedido separado")
    void naoDeveRegistrarExpedicaoParaPedidoSeparado() {

        Pedido pedido = criarPedido();
        pedido.iniciarSeparacao();
        pedido.separar();

        IllegalStateException exception =
                assertThrows(
                        IllegalStateException.class,
                        () -> new Expedicao(pedido)
                );

        assertEquals(
                "Expedição só pode ser registrada para pedido expedido",
                exception.getMessage()
        );
    }

    private Pedido criarPedidoExpedido() {
        Pedido pedido = criarPedido();
        pedido.iniciarSeparacao();
        pedido.separar();
        pedido.expedir();

        return pedido;
    }

    private Pedido criarPedido() {
        return new Pedido(
                List.of(
                        new ItemPedido(UUID.randomUUID(), 1)
                )
        );
    }
}