package application.usecase;

import org.br.application.dto.CriarPedidoDTO;
import org.br.application.usecase.CriarPedidoUseCase;
import org.br.domain.pedido.Pedido;

import org.br.domain.pedido.PedidoRepository;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.mockito.Mockito.verify;

@ExtendWith(MockitoExtension.class)
class CriarPedidoUseCaseTest {

    @Mock
    private PedidoRepository repository;

    @InjectMocks
    private CriarPedidoUseCase useCase;

    @Test
    void deveCriarPedido() {

        CriarPedidoDTO dto = new CriarPedidoDTO();

        Pedido pedido =
                useCase.executar(dto);

        assertNotNull(pedido);

        verify(repository)
                .salvar(pedido);
    }
}
