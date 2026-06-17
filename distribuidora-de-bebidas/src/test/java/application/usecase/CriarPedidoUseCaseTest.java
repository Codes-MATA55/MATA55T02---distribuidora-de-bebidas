package application.usecase;

import org.br.application.dto.CriarPedidoDTO;
import org.br.application.mapper.PedidoMapper;
import org.br.application.usecase.CriarPedidoUseCase;
import org.br.domain.pedido.Pedido;
import org.br.domain.pedido.PedidoRepository;
import org.junit.jupiter.api.DisplayName;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.Mock;
import org.mockito.MockedStatic;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.Collections;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;

@ExtendWith(MockitoExtension.class)
class CriarPedidoUseCaseTest {

    @Mock
    private PedidoRepository repository;

    @Test
    @DisplayName("Deve criar e salvar pedido com sucesso")
    void deveCriarPedidoComSucesso() {

        CriarPedidoUseCase useCase =
                new CriarPedidoUseCase(repository);

        CriarPedidoDTO dto = mock(CriarPedidoDTO.class);

        Pedido pedido = new Pedido(
                Collections.singletonList(
                        mock(org.br.domain.pedido.ItemPedido.class)
                )
        );

        try (MockedStatic<PedidoMapper> mapper =
                     mockStatic(PedidoMapper.class)) {

            mapper.when(() ->
                    PedidoMapper.toEntity(dto)
            ).thenReturn(pedido);

            Pedido resultado =
                    useCase.executar(dto);

            assertNotNull(resultado);
            assertSame(pedido, resultado);

            verify(repository).salvar(pedido);
        }
    }

    @Test
    @DisplayName("Deve retornar o mesmo pedido criado")
    void deveRetornarPedidoCriado() {

        CriarPedidoUseCase useCase =
                new CriarPedidoUseCase(repository);

        CriarPedidoDTO dto = mock(CriarPedidoDTO.class);

        Pedido pedido = new Pedido(
                Collections.singletonList(
                        mock(org.br.domain.pedido.ItemPedido.class)
                )
        );

        try (MockedStatic<PedidoMapper> mapper =
                     mockStatic(PedidoMapper.class)) {

            mapper.when(() ->
                    PedidoMapper.toEntity(dto)
            ).thenReturn(pedido);

            Pedido resultado =
                    useCase.executar(dto);

            assertSame(pedido, resultado);
        }
    }

    @Test
    @DisplayName("Deve salvar pedido uma única vez")
    void deveSalvarPedidoUmaUnicaVez() {

        CriarPedidoUseCase useCase =
                new CriarPedidoUseCase(repository);

        CriarPedidoDTO dto = mock(CriarPedidoDTO.class);

        Pedido pedido = new Pedido(
                Collections.singletonList(
                        mock(org.br.domain.pedido.ItemPedido.class)
                )
        );

        try (MockedStatic<PedidoMapper> mapper =
                     mockStatic(PedidoMapper.class)) {

            mapper.when(() ->
                    PedidoMapper.toEntity(dto)
            ).thenReturn(pedido);

            useCase.executar(dto);

            verify(repository, times(1))
                    .salvar(pedido);

            verifyNoMoreInteractions(repository);
        }
    }

    @Test
    @DisplayName("Deve propagar exceção do mapper")
    void devePropagarExcecaoDoMapper() {

        CriarPedidoUseCase useCase =
                new CriarPedidoUseCase(repository);

        CriarPedidoDTO dto = mock(CriarPedidoDTO.class);

        try (MockedStatic<PedidoMapper> mapper =
                     mockStatic(PedidoMapper.class)) {

            mapper.when(() ->
                    PedidoMapper.toEntity(dto)
            ).thenThrow(
                    new IllegalArgumentException(
                            "Pedido inválido"
                    )
            );

            IllegalArgumentException exception =
                    assertThrows(
                            IllegalArgumentException.class,
                            () -> useCase.executar(dto)
                    );

            assertEquals(
                    "Pedido inválido",
                    exception.getMessage()
            );

            verifyNoInteractions(repository);
        }
    }
}
