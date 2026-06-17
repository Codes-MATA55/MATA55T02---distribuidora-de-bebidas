package domain.pedido;

import org.br.domain.pedido.ItemPedido;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import java.util.UUID;

import static org.junit.jupiter.api.Assertions.*;

class ItemPedidoTest {

    @Test
    @DisplayName("Deve criar item do pedido com sucesso")
    void deveCriarItemPedidoComSucesso() {

        UUID produtoId = UUID.randomUUID();

        ItemPedido item = new ItemPedido(
                produtoId,
                10
        );

        assertEquals(
                produtoId,
                item.getProdutoId()
        );

        assertEquals(
                10,
                item.getQuantidade()
        );
    }

    @Test
    @DisplayName("Deve lançar exceção quando produto for nulo")
    void deveLancarExcecaoQuandoProdutoForNulo() {

        IllegalArgumentException exception =
                assertThrows(
                        IllegalArgumentException.class,
                        () -> new ItemPedido(
                                null,
                                10
                        )
                );

        assertEquals(
                "Produto obrigatório",
                exception.getMessage()
        );
    }

    @Test
    @DisplayName("Deve lançar exceção quando quantidade for zero")
    void deveLancarExcecaoQuandoQuantidadeForZero() {

        UUID produtoId = UUID.randomUUID();

        IllegalArgumentException exception =
                assertThrows(
                        IllegalArgumentException.class,
                        () -> new ItemPedido(
                                produtoId,
                                0
                        )
                );

        assertEquals(
                "Quantidade deve ser maior que zero",
                exception.getMessage()
        );
    }

    @Test
    @DisplayName("Deve lançar exceção quando quantidade for negativa")
    void deveLancarExcecaoQuandoQuantidadeForNegativa() {

        UUID produtoId = UUID.randomUUID();

        IllegalArgumentException exception =
                assertThrows(
                        IllegalArgumentException.class,
                        () -> new ItemPedido(
                                produtoId,
                                -5
                        )
                );

        assertEquals(
                "Quantidade deve ser maior que zero",
                exception.getMessage()
        );
    }

    @Test
    @DisplayName("Deve aceitar quantidade igual a um")
    void deveAceitarQuantidadeIgualAUm() {

        UUID produtoId = UUID.randomUUID();

        ItemPedido item = new ItemPedido(
                produtoId,
                1
        );

        assertEquals(
                1,
                item.getQuantidade()
        );
    }

    @Test
    @DisplayName("Deve manter o mesmo produto informado")
    void deveManterMesmoProdutoInformado() {

        UUID produtoId = UUID.randomUUID();

        ItemPedido item = new ItemPedido(
                produtoId,
                3
        );

        assertSame(
                produtoId,
                item.getProdutoId()
        );
    }
}
