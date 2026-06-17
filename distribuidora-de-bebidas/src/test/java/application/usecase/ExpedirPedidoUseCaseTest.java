package application.usecase;

import org.br.application.usecase.ExpedirPedidoUseCase;
import org.br.domain.expedicao.Expedicao;
import org.br.domain.expedicao.ExpedicaoRepository;
import org.br.domain.pedido.Pedido;
import org.br.domain.pedido.PedidoRepository;
import org.br.domain.pedido.StatusPedido;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.Optional;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class ExpedirPedidoUseCaseTest {

    @Mock
    private PedidoRepository pedidoRepository;

    @Mock
    private ExpedicaoRepository expedicaoRepository;

    @InjectMocks
    private ExpedirPedidoUseCase useCase;

    @Test
    @DisplayName("Deve expedir pedido com sucesso")
    void deveExpedirPedidoComSucesso() {

        UUID pedidoId = UUID.randomUUID();

        Pedido pedido = mock(Pedido.class);

        when(pedidoRepository.buscarPorId(pedidoId))
                .thenReturn(Optional.of(pedido));

        when(pedido.getStatus())
                .thenReturn(StatusPedido.EXPEDIDO);

        when(pedido.getId())
                .thenReturn(pedidoId);

        useCase.executar(pedidoId);

        verify(pedidoRepository)
                .buscarPorId(pedidoId);

        verify(pedido)
                .expedir();

        verify(pedidoRepository)
                .salvar(pedido);

        verify(expedicaoRepository)
                .salvar(any(Expedicao.class));
    }

    @Test
    @DisplayName("Deve buscar pedido apenas uma vez")
    void deveBuscarPedidoUmaUnicaVez() {

        UUID pedidoId = UUID.randomUUID();

        Pedido pedido = mock(Pedido.class);

        when(pedidoRepository.buscarPorId(pedidoId))
                .thenReturn(Optional.of(pedido));

        when(pedido.getStatus())
                .thenReturn(StatusPedido.EXPEDIDO);

        when(pedido.getId())
                .thenReturn(pedidoId);

        useCase.executar(pedidoId);

        verify(pedidoRepository, times(1))
                .buscarPorId(pedidoId);
    }

    @Test
    @DisplayName("Deve salvar pedido e expedicao apenas uma vez")
    void deveSalvarPedidoEExpedicaoUmaUnicaVez() {

        UUID pedidoId = UUID.randomUUID();

        Pedido pedido = mock(Pedido.class);

        when(pedidoRepository.buscarPorId(pedidoId))
                .thenReturn(Optional.of(pedido));

        when(pedido.getStatus())
                .thenReturn(StatusPedido.EXPEDIDO);

        when(pedido.getId())
                .thenReturn(pedidoId);

        useCase.executar(pedidoId);

        verify(pedidoRepository, times(1))
                .salvar(pedido);

        verify(expedicaoRepository, times(1))
                .salvar(any(Expedicao.class));
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

        verify(pedidoRepository)
                .buscarPorId(pedidoId);

        verify(pedidoRepository, never())
                .salvar(any());

        verify(expedicaoRepository, never())
                .salvar(any());
    }

    @Test
    @DisplayName("Não deve salvar quando expedição falhar")
    void naoDeveSalvarQuandoExpedicaoFalhar() {

        UUID pedidoId = UUID.randomUUID();

        Pedido pedido = mock(Pedido.class);

        when(pedidoRepository.buscarPorId(pedidoId))
                .thenReturn(Optional.of(pedido));

        doThrow(
                new IllegalStateException(
                        "Somente pedidos separados podem ser expedidos"
                )
        ).when(pedido).expedir();

        IllegalStateException exception =
                assertThrows(
                        IllegalStateException.class,
                        () -> useCase.executar(pedidoId)
                );

        assertEquals(
                "Somente pedidos separados podem ser expedidos",
                exception.getMessage()
        );

        verify(pedido)
                .expedir();

        verify(pedidoRepository, never())
                .salvar(any());

        verify(expedicaoRepository, never())
                .salvar(any());
    }

    @Test
    @DisplayName("Deve propagar exceção da regra de negócio")
    void devePropagarExcecaoDaRegraDeNegocio() {

        UUID pedidoId = UUID.randomUUID();

        Pedido pedido = mock(Pedido.class);

        when(pedidoRepository.buscarPorId(pedidoId))
                .thenReturn(Optional.of(pedido));

        doThrow(new IllegalStateException("Pedido inválido"))
                .when(pedido)
                .expedir();

        IllegalStateException exception =
                assertThrows(
                        IllegalStateException.class,
                        () -> useCase.executar(pedidoId)
                );

        assertEquals(
                "Pedido inválido",
                exception.getMessage()
        );

        verify(pedidoRepository, never())
                .salvar(any());

        verify(expedicaoRepository, never())
                .salvar(any());
    }
}
