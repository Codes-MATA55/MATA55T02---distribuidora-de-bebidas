package domain.pedido;

import org.br.domain.pedido.ItemPedido;
import org.br.domain.pedido.Pedido;
import org.br.domain.pedido.StatusPedido;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import java.util.List;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.mock;

class PedidoTest {

    @Test
    @DisplayName("Deve criar pedido com sucesso")
    void deveCriarPedidoComSucesso() {

        ItemPedido item = mock(ItemPedido.class);

        Pedido pedido = new Pedido(List.of(item));

        assertNotNull(pedido.getId());
        assertEquals(StatusPedido.CRIADO, pedido.getStatus());
        assertEquals(1, pedido.getItens().size());
    }

    @Test
    @DisplayName("Deve lançar exceção quando lista de itens for nula")
    void deveLancarExcecaoQuandoItensForemNulos() {

        IllegalArgumentException exception =
                assertThrows(
                        IllegalArgumentException.class,
                        () -> new Pedido(null)
                );

        assertEquals(
                "Pedido deve possuir pelo menos um item",
                exception.getMessage()
        );
    }

    @Test
    @DisplayName("Deve lançar exceção quando lista de itens estiver vazia")
    void deveLancarExcecaoQuandoItensForemVazios() {

        IllegalArgumentException exception =
                assertThrows(
                        IllegalArgumentException.class,
                        () -> new Pedido(List.of())
                );

        assertEquals(
                "Pedido deve possuir pelo menos um item",
                exception.getMessage()
        );
    }

    @Test
    @DisplayName("Deve mudar para aguardando estoque")
    void deveMudarParaAguardandoEstoque() {

        Pedido pedido =
                new Pedido(List.of(mock(ItemPedido.class)));

        pedido.aguardarEstoque();

        assertEquals(
                StatusPedido.AGUARDANDO_ESTOQUE,
                pedido.getStatus()
        );
    }

    @Test
    @DisplayName("Não deve permitir aguardar estoque fora do estado criado")
    void naoDevePermitirAguardarEstoqueForaDoEstadoCriado() {

        Pedido pedido =
                new Pedido(List.of(mock(ItemPedido.class)));

        pedido.aguardarEstoque();

        IllegalStateException exception =
                assertThrows(
                        IllegalStateException.class,
                        pedido::aguardarEstoque
                );

        assertEquals(
                "Somente pedidos criados podem aguardar estoque",
                exception.getMessage()
        );
    }

    @Test
    @DisplayName("Deve iniciar separação a partir de criado")
    void deveIniciarSeparacaoAPartirDeCriado() {

        Pedido pedido =
                new Pedido(List.of(mock(ItemPedido.class)));

        pedido.iniciarSeparacao();

        assertEquals(
                StatusPedido.EM_SEPARACAO,
                pedido.getStatus()
        );
    }

    @Test
    @DisplayName("Deve iniciar separação a partir de aguardando estoque")
    void deveIniciarSeparacaoAPartirDeAguardandoEstoque() {

        Pedido pedido =
                new Pedido(List.of(mock(ItemPedido.class)));

        pedido.aguardarEstoque();

        pedido.iniciarSeparacao();

        assertEquals(
                StatusPedido.EM_SEPARACAO,
                pedido.getStatus()
        );
    }

    @Test
    @DisplayName("Não deve iniciar separação em estado inválido")
    void naoDeveIniciarSeparacaoEmEstadoInvalido() {

        Pedido pedido =
                new Pedido(List.of(mock(ItemPedido.class)));

        pedido.iniciarSeparacao();

        IllegalStateException exception =
                assertThrows(
                        IllegalStateException.class,
                        pedido::iniciarSeparacao
                );

        assertEquals(
                "Pedido não pode entrar em separação",
                exception.getMessage()
        );
    }

    @Test
    @DisplayName("Deve separar pedido")
    void deveSepararPedido() {

        Pedido pedido =
                new Pedido(List.of(mock(ItemPedido.class)));

        pedido.iniciarSeparacao();

        pedido.separar();

        assertEquals(
                StatusPedido.SEPARADO,
                pedido.getStatus()
        );
    }

    @Test
    @DisplayName("Não deve separar pedido fora de EM_SEPARACAO")
    void naoDeveSepararPedidoForaDeEmSeparacao() {

        Pedido pedido =
                new Pedido(List.of(mock(ItemPedido.class)));

        IllegalStateException exception =
                assertThrows(
                        IllegalStateException.class,
                        pedido::separar
                );

        assertEquals(
                "Pedido deve estar em separação",
                exception.getMessage()
        );
    }

    @Test
    @DisplayName("Deve expedir pedido separado")
    void deveExpedirPedidoSeparado() {

        Pedido pedido =
                new Pedido(List.of(mock(ItemPedido.class)));

        pedido.iniciarSeparacao();
        pedido.separar();
        pedido.expedir();

        assertEquals(
                StatusPedido.EXPEDIDO,
                pedido.getStatus()
        );
    }

    @Test
    @DisplayName("Não deve expedir pedido fora de separado")
    void naoDeveExpedirPedidoForaDeSeparado() {

        Pedido pedido =
                new Pedido(List.of(mock(ItemPedido.class)));

        IllegalStateException exception =
                assertThrows(
                        IllegalStateException.class,
                        pedido::expedir
                );

        assertEquals(
                "Somente pedidos separados podem ser expedidos",
                exception.getMessage()
        );
    }

    @Test
    @DisplayName("Deve cancelar pedido criado")
    void deveCancelarPedidoCriado() {

        Pedido pedido =
                new Pedido(List.of(mock(ItemPedido.class)));

        pedido.cancelar();

        assertEquals(
                StatusPedido.CANCELADO,
                pedido.getStatus()
        );
    }

    @Test
    @DisplayName("Deve cancelar pedido aguardando estoque")
    void deveCancelarPedidoAguardandoEstoque() {

        Pedido pedido =
                new Pedido(List.of(mock(ItemPedido.class)));

        pedido.aguardarEstoque();

        pedido.cancelar();

        assertEquals(
                StatusPedido.CANCELADO,
                pedido.getStatus()
        );
    }

    @Test
    @DisplayName("Deve cancelar pedido em separação")
    void deveCancelarPedidoEmSeparacao() {

        Pedido pedido =
                new Pedido(List.of(mock(ItemPedido.class)));

        pedido.iniciarSeparacao();

        pedido.cancelar();

        assertEquals(
                StatusPedido.CANCELADO,
                pedido.getStatus()
        );
    }

    @Test
    @DisplayName("Deve cancelar pedido separado")
    void deveCancelarPedidoSeparado() {

        Pedido pedido =
                new Pedido(List.of(mock(ItemPedido.class)));

        pedido.iniciarSeparacao();
        pedido.separar();

        pedido.cancelar();

        assertEquals(
                StatusPedido.CANCELADO,
                pedido.getStatus()
        );
    }

    @Test
    @DisplayName("Não deve cancelar pedido expedido")
    void naoDeveCancelarPedidoExpedido() {

        Pedido pedido =
                new Pedido(List.of(mock(ItemPedido.class)));

        pedido.iniciarSeparacao();
        pedido.separar();
        pedido.expedir();

        IllegalStateException exception =
                assertThrows(
                        IllegalStateException.class,
                        pedido::cancelar
                );

        assertEquals(
                "Pedido expedido não pode ser cancelado",
                exception.getMessage()
        );
    }

    @Test
    @DisplayName("Lista de itens deve ser imutável")
    void listaDeItensDeveSerImutavel() {

        Pedido pedido =
                new Pedido(List.of(mock(ItemPedido.class)));

        assertThrows(
                UnsupportedOperationException.class,
                () -> pedido.getItens().add(mock(ItemPedido.class))
        );
    }
}
