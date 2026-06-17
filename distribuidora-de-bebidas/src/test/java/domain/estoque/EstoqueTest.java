package domain.estoque;

import org.br.domain.estoque.Estoque;
import org.br.domain.estoque.Produto;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.Mockito.mock;
import static org.mockito.Mockito.when;

class EstoqueTest {

    @Test
    @DisplayName("Deve criar estoque com sucesso")
    void deveCriarEstoqueComSucesso() {

        Produto produto = mock(Produto.class);

        Estoque estoque = new Estoque(produto, 100);

        assertEquals(produto, estoque.getProduto());
        assertEquals(100, estoque.getQuantidadeDisponivel());
    }

    @Test
    @DisplayName("Deve lançar exceção quando produto for nulo")
    void deveLancarExcecaoQuandoProdutoForNulo() {

        IllegalArgumentException exception =
                assertThrows(
                        IllegalArgumentException.class,
                        () -> new Estoque(null, 10)
                );

        assertEquals(
                "Produto é obrigatório",
                exception.getMessage()
        );
    }

    @Test
    @DisplayName("Deve lançar exceção quando quantidade inicial for negativa")
    void deveLancarExcecaoQuandoQuantidadeInicialForNegativa() {

        Produto produto = mock(Produto.class);

        IllegalArgumentException exception =
                assertThrows(
                        IllegalArgumentException.class,
                        () -> new Estoque(produto, -1)
                );

        assertEquals(
                "Quantidade disponível não pode ser negativa",
                exception.getMessage()
        );
    }

    @Test
    @DisplayName("Deve reservar estoque com sucesso")
    void deveReservarEstoqueComSucesso() {

        Produto produto = mock(Produto.class);

        Estoque estoque = new Estoque(produto, 100);

        estoque.reservar(30);

        assertEquals(
                70,
                estoque.getQuantidadeDisponivel()
        );
    }

    @Test
    @DisplayName("Deve zerar estoque quando reservar toda quantidade")
    void deveReservarTodaQuantidadeDisponivel() {

        Produto produto = mock(Produto.class);

        Estoque estoque = new Estoque(produto, 50);

        estoque.reservar(50);

        assertEquals(
                0,
                estoque.getQuantidadeDisponivel()
        );
    }

    @Test
    @DisplayName("Deve lançar exceção ao reservar quantidade zero")
    void deveLancarExcecaoAoReservarQuantidadeZero() {

        Produto produto = mock(Produto.class);

        Estoque estoque = new Estoque(produto, 100);

        IllegalArgumentException exception =
                assertThrows(
                        IllegalArgumentException.class,
                        () -> estoque.reservar(0)
                );

        assertEquals(
                "Quantidade deve ser maior que zero",
                exception.getMessage()
        );
    }

    @Test
    @DisplayName("Deve lançar exceção ao reservar quantidade negativa")
    void deveLancarExcecaoAoReservarQuantidadeNegativa() {

        Produto produto = mock(Produto.class);

        Estoque estoque = new Estoque(produto, 100);

        IllegalArgumentException exception =
                assertThrows(
                        IllegalArgumentException.class,
                        () -> estoque.reservar(-10)
                );

        assertEquals(
                "Quantidade deve ser maior que zero",
                exception.getMessage()
        );
    }

    @Test
    @DisplayName("Deve lançar exceção quando estoque for insuficiente")
    void deveLancarExcecaoQuandoEstoqueForInsuficiente() {

        Produto produto = mock(Produto.class);

        when(produto.getNome())
                .thenReturn("Coca-Cola");

        Estoque estoque = new Estoque(produto, 10);

        IllegalArgumentException exception =
                assertThrows(
                        IllegalArgumentException.class,
                        () -> estoque.reservar(20)
                );

        assertEquals(
                "Estoque insuficiente para o produto Coca-Cola",
                exception.getMessage()
        );

        assertEquals(
                10,
                estoque.getQuantidadeDisponivel()
        );
    }

    @Test
    @DisplayName("Deve adicionar estoque com sucesso")
    void deveAdicionarEstoqueComSucesso() {

        Produto produto = mock(Produto.class);

        Estoque estoque = new Estoque(produto, 100);

        estoque.adicionar(50);

        assertEquals(
                150,
                estoque.getQuantidadeDisponivel()
        );
    }

    @Test
    @DisplayName("Deve lançar exceção ao adicionar quantidade zero")
    void deveLancarExcecaoAoAdicionarQuantidadeZero() {

        Produto produto = mock(Produto.class);

        Estoque estoque = new Estoque(produto, 100);

        IllegalArgumentException exception =
                assertThrows(
                        IllegalArgumentException.class,
                        () -> estoque.adicionar(0)
                );

        assertEquals(
                "Quantidade deve ser maior que zero",
                exception.getMessage()
        );
    }

    @Test
    @DisplayName("Deve lançar exceção ao adicionar quantidade negativa")
    void deveLancarExcecaoAoAdicionarQuantidadeNegativa() {

        Produto produto = mock(Produto.class);

        Estoque estoque = new Estoque(produto, 100);

        IllegalArgumentException exception =
                assertThrows(
                        IllegalArgumentException.class,
                        () -> estoque.adicionar(-10)
                );

        assertEquals(
                "Quantidade deve ser maior que zero",
                exception.getMessage()
        );
    }
}