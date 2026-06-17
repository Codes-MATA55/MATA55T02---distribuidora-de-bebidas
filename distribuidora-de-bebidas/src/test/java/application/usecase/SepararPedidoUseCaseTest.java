package application.usecase;

import org.br.application.usecase.SepararPedidoUseCase;
import org.br.domain.pedido.Pedido;
import org.br.domain.pedido.PedidoRepository;
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
class SepararPedidoUseCaseTest {

    @Mock
    private PedidoRepository pedidoRepository;

    @InjectMocks
    private SepararPedidoUseCase useCase;

    @Test
    @DisplayName("Deve separar pedido com sucesso")
    void deveSepararPedidoComSucesso() {

        UUID pedidoId = UUID.randomUUID();

        Pedido pedido = mock(Pedido.class);

        when(pedidoRepository.buscarPorId(pedidoId))
                .thenReturn(Optional.of(pedido));

        useCase.executar(pedidoId);

        verify(pedidoRepository)
                .buscarPorId(pedidoId);

        verify(pedido)
                .separar();

        verify(pedidoRepository)
                .salvar(pedido);
    }

    @Test
    @DisplayName("Deve chamar separar apenas uma vez")
    void deveChamarSepararUmaVez() {

        UUID pedidoId = UUID.randomUUID();

        Pedido pedido = mock(Pedido.class);

        when(pedidoRepository.buscarPorId(pedidoId))
                .thenReturn(Optional.of(pedido));

        useCase.executar(pedidoId);

        verify(pedido, times(1))
                .separar();
    }

    @Test
    @DisplayName("Deve salvar pedido apenas uma vez")
    void deveSalvarPedidoUmaVez() {

        UUID pedidoId = UUID.randomUUID();

        Pedido pedido = mock(Pedido.class);

        when(pedidoRepository.buscarPorId(pedidoId))
                .thenReturn(Optional.of(pedido));

        useCase.executar(pedidoId);

        verify(pedidoRepository, times(1))
                .salvar(pedido);
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
    }

    @Test
    @DisplayName("Não deve salvar pedido quando separação falhar")
    void naoDeveSalvarPedidoQuandoSeparacaoFalhar() {

        UUID pedidoId = UUID.randomUUID();

        Pedido pedido = mock(Pedido.class);

        when(pedidoRepository.buscarPorId(pedidoId))
                .thenReturn(Optional.of(pedido));

        doThrow(
                new IllegalStateException(
                        "Pedido deve estar em separação"
                )
        ).when(pedido).separar();

        IllegalStateException exception =
                assertThrows(
                        IllegalStateException.class,
                        () -> useCase.executar(pedidoId)
                );

        assertEquals(
                "Pedido deve estar em separação",
                exception.getMessage()
        );

        verify(pedido)
                .separar();

        verify(pedidoRepository, never())
                .salvar(any());
    }

    @Test
    @DisplayName("Deve propagar exceção da regra de negócio")
    void devePropagarExcecaoDaRegraDeNegocio() {

        UUID pedidoId = UUID.randomUUID();

        Pedido pedido = mock(Pedido.class);

        when(pedidoRepository.buscarPorId(pedidoId))
                .thenReturn(Optional.of(pedido));

        doThrow(
                new IllegalStateException(
                        "Estado inválido para separação"
                )
        ).when(pedido).separar();

        IllegalStateException exception =
                assertThrows(
                        IllegalStateException.class,
                        () -> useCase.executar(pedidoId)
                );

        assertEquals(
                "Estado inválido para separação",
                exception.getMessage()
        );

        verify(pedidoRepository, never())
                .salvar(any());
    }
}
