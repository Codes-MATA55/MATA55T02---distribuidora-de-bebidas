package application.usecase;

import org.br.application.dto.PedidoResponseDTO;
import org.br.application.usecase.BuscarPedidoUseCase;
import org.br.domain.pedido.Pedido;
import org.br.domain.pedido.PedidoRepository;
import org.br.domain.pedido.StatusPedido;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.lang.reflect.Field;
import java.util.Collections;
import java.util.Optional;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class BuscarPedidoUseCaseTest {

    @Mock
    private PedidoRepository pedidoRepository;

    @InjectMocks
    private BuscarPedidoUseCase useCase;

    private UUID pedidoId;
    private Pedido pedido;

    @BeforeEach
    void setup() throws Exception {

        pedidoId = UUID.randomUUID();

        pedido = new Pedido(Collections.singletonList(
                mock(org.br.domain.pedido.ItemPedido.class)
        ));

        Field idField = Pedido.class.getDeclaredField("id");
        idField.setAccessible(true);
        idField.set(pedido, pedidoId);

        Field statusField = Pedido.class.getDeclaredField("status");
        statusField.setAccessible(true);
        statusField.set(pedido, StatusPedido.CRIADO);
    }

    @Test
    @DisplayName("Deve retornar pedido quando encontrado")
    void deveRetornarPedidoQuandoEncontrado() {

        when(pedidoRepository.buscarPorId(pedidoId))
                .thenReturn(Optional.of(pedido));

        PedidoResponseDTO response =
                useCase.executar(pedidoId);

        assertNotNull(response);
        assertEquals(pedidoId, response.getId());
        assertEquals(StatusPedido.CRIADO, response.getStatus());

        verify(pedidoRepository)
                .buscarPorId(pedidoId);
    }

    @Test
    @DisplayName("Deve retornar id correto do pedido")
    void deveRetornarIdCorreto() {

        when(pedidoRepository.buscarPorId(pedidoId))
                .thenReturn(Optional.of(pedido));

        PedidoResponseDTO response =
                useCase.executar(pedidoId);

        assertEquals(pedidoId, response.getId());
    }

    @Test
    @DisplayName("Deve retornar status correto do pedido")
    void deveRetornarStatusCorreto() {

        when(pedidoRepository.buscarPorId(pedidoId))
                .thenReturn(Optional.of(pedido));

        PedidoResponseDTO response =
                useCase.executar(pedidoId);

        assertEquals(StatusPedido.CRIADO, response.getStatus());
    }

    @Test
    @DisplayName("Deve lançar exceção quando pedido não existir")
    void deveLancarExcecaoQuandoPedidoNaoExistir() {

        when(pedidoRepository.buscarPorId(pedidoId))
                .thenReturn(Optional.empty());

        IllegalArgumentException exception =
                assertThrows(
                        IllegalArgumentException.class,
                        () -> useCase.executar(pedidoId)
                );

        assertEquals(
                "Pedido não encontrado: " + pedidoId,
                exception.getMessage()
        );

        verify(pedidoRepository)
                .buscarPorId(pedidoId);
    }

    @Test
    @DisplayName("Deve consultar o repositório apenas uma vez")
    void deveConsultarRepositorioUmaVez() {

        when(pedidoRepository.buscarPorId(pedidoId))
                .thenReturn(Optional.of(pedido));

        useCase.executar(pedidoId);

        verify(pedidoRepository, times(1))
                .buscarPorId(pedidoId);

        verifyNoMoreInteractions(pedidoRepository);
    }
}
