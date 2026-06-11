package application.usecase;

import org.br.application.dto.PedidoResponseDTO;
import org.br.application.usecase.BuscarPedidoUseCase;
import org.br.domain.pedido.Pedido;
import org.br.domain.pedido.PedidoRepository;
import org.br.domain.pedido.StatusPedido;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.Collections;
import java.util.Optional;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.mockito.Mockito.when;

@ExtendWith(MockitoExtension.class)
class BuscarPedidoUseCaseTest {

    @Mock
    private PedidoRepository pedidoRepository;

    @InjectMocks
    private BuscarPedidoUseCase useCase;

    @Test
    void deveBuscarPedidoPorId() {

        UUID id = UUID.randomUUID();

        Pedido pedido = new Pedido(Collections.emptyList());
        pedido.setId(id);
        pedido.setStatus(StatusPedido.CRIADO);

        when(pedidoRepository.buscarPorId(id))
                .thenReturn(Optional.of(pedido));

        PedidoResponseDTO response =
                useCase.executar(id);

        assertEquals(id, response.getId());
        assertEquals(StatusPedido.CRIADO,
                response.getStatus());
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
