package application.usecase;

import org.br.application.usecase.ReservarEstoqueUseCase;
import org.br.domain.estoque.Estoque;
import org.br.domain.estoque.EstoqueRepository;
import org.br.domain.pedido.ItemPedido;
import org.br.domain.pedido.Pedido;
import org.br.domain.pedido.PedidoRepository;
import org.br.domain.pedido.StatusPedido;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class ReservarEstoqueUseCaseTest {

    @Mock
    private PedidoRepository pedidoRepository;

    @Mock
    private EstoqueRepository estoqueRepository;

    @InjectMocks
    private ReservarEstoqueUseCase useCase;

    @Test
    @DisplayName("Deve reservar estoque com sucesso")
    void deveReservarEstoqueComSucesso() {

        UUID pedidoId = UUID.randomUUID();
        UUID produtoId = UUID.randomUUID();

        Pedido pedido = mock(Pedido.class);
        ItemPedido item = mock(ItemPedido.class);
        Estoque estoque = mock(Estoque.class);

        when(pedidoRepository.buscarPorId(pedidoId))
                .thenReturn(Optional.of(pedido));

        when(pedido.getStatus())
                .thenReturn(StatusPedido.CRIADO);

        when(pedido.getItens())
                .thenReturn(List.of(item));

        when(item.getProdutoId())
                .thenReturn(produtoId);

        when(item.getQuantidade())
                .thenReturn(5);

        when(estoqueRepository.buscarPorProdutoId(produtoId))
                .thenReturn(Optional.of(estoque));

        useCase.executar(pedidoId);

        verify(estoque).reservar(5);
        verify(estoqueRepository).salvar(estoque);
        verify(pedido).iniciarSeparacao();
        verify(pedidoRepository).salvar(pedido);
    }

    @Test
    @DisplayName("Deve aceitar pedido aguardando estoque")
    void deveAceitarPedidoAguardandoEstoque() {

        UUID pedidoId = UUID.randomUUID();

        Pedido pedido = mock(Pedido.class);

        when(pedidoRepository.buscarPorId(pedidoId))
                .thenReturn(Optional.of(pedido));

        when(pedido.getStatus())
                .thenReturn(StatusPedido.AGUARDANDO_ESTOQUE);

        when(pedido.getItens())
                .thenReturn(List.of());

        useCase.executar(pedidoId);

        verify(pedido).iniciarSeparacao();
        verify(pedidoRepository).salvar(pedido);
    }

    @Test
    @DisplayName("Deve lançar exceção quando pedido não existir")
    void deveLancarExcecaoQuandoPedidoNaoExistir() {

        UUID pedidoId = UUID.randomUUID();

        when(pedidoRepository.buscarPorId(pedidoId))
                .thenReturn(Optional.empty());

        IllegalArgumentException exception =
                assertThrows(
                        IllegalArgumentException.class,
                        () -> useCase.executar(pedidoId)
                );

        assertEquals(
                "Pedido não encontrado",
                exception.getMessage()
        );

        verifyNoInteractions(estoqueRepository);
    }

    @Test
    @DisplayName("Deve lançar exceção para pedido em estado inválido")
    void deveLancarExcecaoQuandoPedidoJaReservado() {

        UUID pedidoId = UUID.randomUUID();

        Pedido pedido = mock(Pedido.class);

        when(pedidoRepository.buscarPorId(pedidoId))
                .thenReturn(Optional.of(pedido));

        when(pedido.getStatus())
                .thenReturn(StatusPedido.EM_SEPARACAO);

        IllegalStateException exception =
                assertThrows(
                        IllegalStateException.class,
                        () -> useCase.executar(pedidoId)
                );

        assertEquals(
                "Pedido já foi reservado ou não pode ser reservado",
                exception.getMessage()
        );

        verifyNoInteractions(estoqueRepository);
        verify(pedidoRepository, never()).salvar(any());
    }

    @Test
    @DisplayName("Deve lançar exceção quando estoque não existir")
    void deveLancarExcecaoQuandoEstoqueNaoExistir() {

        UUID pedidoId = UUID.randomUUID();
        UUID produtoId = UUID.randomUUID();

        Pedido pedido = mock(Pedido.class);
        ItemPedido item = mock(ItemPedido.class);

        when(pedidoRepository.buscarPorId(pedidoId))
                .thenReturn(Optional.of(pedido));

        when(pedido.getStatus())
                .thenReturn(StatusPedido.CRIADO);

        when(pedido.getItens())
                .thenReturn(List.of(item));

        when(item.getProdutoId())
                .thenReturn(produtoId);

        when(estoqueRepository.buscarPorProdutoId(produtoId))
                .thenReturn(Optional.empty());

        IllegalArgumentException exception =
                assertThrows(
                        IllegalArgumentException.class,
                        () -> useCase.executar(pedidoId)
                );

        assertTrue(
                exception.getMessage()
                        .contains("Estoque não encontrado para o produto")
        );

        verify(pedidoRepository, never()).salvar(any());
    }

    @Test
    @DisplayName("Não deve salvar pedido quando reserva falhar")
    void naoDeveSalvarPedidoQuandoReservaFalhar() {

        UUID pedidoId = UUID.randomUUID();
        UUID produtoId = UUID.randomUUID();

        Pedido pedido = mock(Pedido.class);
        ItemPedido item = mock(ItemPedido.class);
        Estoque estoque = mock(Estoque.class);

        when(pedidoRepository.buscarPorId(pedidoId))
                .thenReturn(Optional.of(pedido));

        when(pedido.getStatus())
                .thenReturn(StatusPedido.CRIADO);

        when(pedido.getItens())
                .thenReturn(List.of(item));

        when(item.getProdutoId())
                .thenReturn(produtoId);

        when(item.getQuantidade())
                .thenReturn(10);

        when(estoqueRepository.buscarPorProdutoId(produtoId))
                .thenReturn(Optional.of(estoque));

        doThrow(
                new IllegalArgumentException(
                        "Estoque insuficiente"
                )
        ).when(estoque).reservar(10);

        assertThrows(
                IllegalArgumentException.class,
                () -> useCase.executar(pedidoId)
        );

        verify(pedidoRepository, never())
                .salvar(any());

        verify(pedido, never())
                .iniciarSeparacao();
    }

    @Test
    @DisplayName("Deve reservar estoque para todos os itens")
    void deveReservarTodosOsItens() {

        UUID pedidoId = UUID.randomUUID();

        UUID produto1 = UUID.randomUUID();
        UUID produto2 = UUID.randomUUID();

        Pedido pedido = mock(Pedido.class);

        ItemPedido item1 = mock(ItemPedido.class);
        ItemPedido item2 = mock(ItemPedido.class);

        Estoque estoque1 = mock(Estoque.class);
        Estoque estoque2 = mock(Estoque.class);

        when(pedidoRepository.buscarPorId(pedidoId))
                .thenReturn(Optional.of(pedido));

        when(pedido.getStatus())
                .thenReturn(StatusPedido.CRIADO);

        when(pedido.getItens())
                .thenReturn(List.of(item1, item2));

        when(item1.getProdutoId()).thenReturn(produto1);
        when(item2.getProdutoId()).thenReturn(produto2);

        when(item1.getQuantidade()).thenReturn(3);
        when(item2.getQuantidade()).thenReturn(7);

        when(estoqueRepository.buscarPorProdutoId(produto1))
                .thenReturn(Optional.of(estoque1));

        when(estoqueRepository.buscarPorProdutoId(produto2))
                .thenReturn(Optional.of(estoque2));

        useCase.executar(pedidoId);

        verify(estoque1).reservar(3);
        verify(estoque2).reservar(7);

        verify(estoqueRepository).salvar(estoque1);
        verify(estoqueRepository).salvar(estoque2);

        verify(pedido).iniciarSeparacao();
        verify(pedidoRepository).salvar(pedido);
    }
}