package api;

import org.br.api.PedidoController;
import org.br.application.dto.CriarPedidoDTO;
import org.br.application.dto.PedidoResponseDTO;
import org.br.application.usecase.*;
import org.br.domain.pedido.Pedido;
import org.br.domain.pedido.StatusPedido;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.mockito.Mock;
import org.mockito.MockitoAnnotations;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;

import java.util.UUID;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

class PedidoControllerTest {

    @Mock
    private CriarPedidoUseCase criarPedidoUseCase;

    @Mock
    private BuscarPedidoUseCase buscarPedidoUseCase;

    @Mock
    private ReservarEstoqueUseCase reservarEstoqueUseCase;

    @Mock
    private ExpedirPedidoUseCase expedirPedidoUseCase;

    @Mock
    private SepararPedidoUseCase separarPedidoUseCase;

    private PedidoController controller;

    @BeforeEach
    void setup() {

        MockitoAnnotations.openMocks(this);

        controller = new PedidoController(
                criarPedidoUseCase,
                buscarPedidoUseCase,
                reservarEstoqueUseCase,
                expedirPedidoUseCase,
                separarPedidoUseCase
        );
    }

    @Test
    @DisplayName("Deve criar pedido com sucesso")
    void deveCriarPedidoComSucesso() {

        CriarPedidoDTO dto = new CriarPedidoDTO();

        Pedido pedido = mock(Pedido.class);

        UUID id = UUID.randomUUID();

        when(pedido.getId()).thenReturn(id);
        when(pedido.getStatus()).thenReturn(StatusPedido.CRIADO);

        when(criarPedidoUseCase.executar(dto))
                .thenReturn(pedido);

        ResponseEntity<PedidoResponseDTO> response =
                controller.criarPedido(dto);

        assertEquals(HttpStatus.CREATED, response.getStatusCode());

        assertNotNull(response.getBody());

        assertEquals(
                id,
                response.getBody().getId()
        );

        assertEquals(
                StatusPedido.CRIADO,
                response.getBody().getStatus()
        );

        verify(criarPedidoUseCase)
                .executar(dto);
    }

    @Test
    @DisplayName("Deve buscar pedido por id")
    void deveBuscarPedidoPorId() {

        UUID id = UUID.randomUUID();

        PedidoResponseDTO dto =
                new PedidoResponseDTO(
                        id,
                        StatusPedido.CRIADO
                );

        when(buscarPedidoUseCase.executar(id))
                .thenReturn(dto);

        ResponseEntity<PedidoResponseDTO> response =
                controller.buscarPorId(id);

        assertEquals(HttpStatus.OK, response.getStatusCode());

        assertEquals(dto, response.getBody());

        verify(buscarPedidoUseCase)
                .executar(id);
    }

    @Test
    @DisplayName("Deve reservar estoque")
    void deveReservarEstoque() {

        UUID id = UUID.randomUUID();

        ResponseEntity<Void> response =
                controller.reservar(id);

        assertEquals(HttpStatus.OK, response.getStatusCode());

        verify(reservarEstoqueUseCase)
                .executar(id);
    }

    @Test
    @DisplayName("Deve expedir pedido")
    void deveExpedirPedido() {

        UUID id = UUID.randomUUID();

        ResponseEntity<Void> response =
                controller.expedirPedido(id);

        assertEquals(HttpStatus.OK, response.getStatusCode());

        verify(expedirPedidoUseCase)
                .executar(id);
    }

    @Test
    @DisplayName("Deve separar pedido")
    void deveSepararPedido() {

        UUID id = UUID.randomUUID();

        ResponseEntity<Void> response =
                controller.separar(id);

        assertEquals(HttpStatus.OK, response.getStatusCode());

        verify(separarPedidoUseCase)
                .executar(id);
    }

    @Test
    @DisplayName("Deve propagar exceção ao buscar pedido")
    void devePropagarExcecaoAoBuscarPedido() {

        UUID id = UUID.randomUUID();

        when(buscarPedidoUseCase.executar(id))
                .thenThrow(
                        new IllegalArgumentException(
                                "Pedido não encontrado"
                        )
                );

        IllegalArgumentException exception =
                assertThrows(
                        IllegalArgumentException.class,
                        () -> controller.buscarPorId(id)
                );

        assertEquals(
                "Pedido não encontrado",
                exception.getMessage()
        );
    }

    @Test
    @DisplayName("Deve propagar exceção ao reservar estoque")
    void devePropagarExcecaoAoReservarEstoque() {

        UUID id = UUID.randomUUID();

        doThrow(
                new IllegalStateException(
                        "Pedido inválido"
                )
        ).when(reservarEstoqueUseCase)
                .executar(id);

        IllegalStateException exception =
                assertThrows(
                        IllegalStateException.class,
                        () -> controller.reservar(id)
                );

        assertEquals(
                "Pedido inválido",
                exception.getMessage()
        );
    }
}
