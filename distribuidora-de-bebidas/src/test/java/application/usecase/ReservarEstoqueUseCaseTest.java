package application.usecase;

import org.br.application.usecase.ReservarEstoqueUseCase;
import org.br.domain.estoque.Estoque;
import org.br.domain.estoque.EstoqueRepository;
import org.br.domain.estoque.Produto;
import org.br.domain.pedido.ItemPedido;
import org.br.domain.pedido.Pedido;
import org.br.domain.pedido.PedidoRepository;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

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
    void deveReservarEstoque() {

        UUID produtoId = UUID.randomUUID();
        UUID pedidoId = UUID.randomUUID();

        Produto produto = new Produto();
        produto.setId(produtoId);

        ItemPedido item =
                new ItemPedido(produto.getId(), 5);

        Pedido pedido =
                new Pedido(List.of(item));

        Estoque estoque =
                spy(new Estoque());

        estoque.setProduto(produto);
        estoque.setQuantidadeDisponivel(20);

        when(pedidoRepository.buscarPorId(pedidoId))
                .thenReturn(Optional.of(pedido));

        when(estoqueRepository.buscarPorProdutoId(produtoId))
                .thenReturn(Optional.of(estoque));

        useCase.executar(pedidoId);

        verify(estoque)
                .reservar(5);

        verify(estoqueRepository)
                .salvar(estoque);

        verify(pedidoRepository)
                .salvar(pedido);
    }
}