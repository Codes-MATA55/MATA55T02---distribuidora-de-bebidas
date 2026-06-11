package application.usecase;

import org.br.application.usecase.ExpedirPedidoUseCase;
import org.br.domain.pedido.Pedido;
import org.br.domain.pedido.PedidoRepository;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.Collections;
import java.util.Optional;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class ExpedirPedidoUseCaseTest {

    @Mock
    private PedidoRepository pedidoRepository;

    @InjectMocks
    private ExpedirPedidoUseCase useCase;

    @Test
    void deveExpedirPedido() {

        UUID id = UUID.randomUUID();

        Pedido pedido =
                spy(new Pedido(Collections.emptyList()));

        when(pedidoRepository.buscarPorId(id))
                .thenReturn(Optional.of(pedido));

        useCase.executar(id);

        verify(pedido).expedir();

        verify(pedidoRepository)
                .salvar(pedido);
    }

    @Test
    void deveLancarExcecaoQuandoPedidoNaoExistir() {

        UUID id = UUID.randomUUID();

        when(pedidoRepository.buscarPorId(id))
                .thenReturn(Optional.empty());

        assertThrows(
                IllegalArgumentException.class,
                () -> useCase.executar(id)
        );
    }
}
