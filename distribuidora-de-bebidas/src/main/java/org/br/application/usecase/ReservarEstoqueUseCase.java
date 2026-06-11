package org.br.application.usecase;

import org.br.domain.estoque.Estoque;
import org.br.domain.estoque.EstoqueRepository;
import org.br.domain.pedido.ItemPedido;
import org.br.domain.pedido.Pedido;
import org.br.domain.pedido.PedidoRepository;
import org.springframework.stereotype.Service;

import java.util.UUID;

@Service
public class ReservarEstoqueUseCase {

    private final PedidoRepository pedidoRepository;
    private final EstoqueRepository estoqueRepository;

    public ReservarEstoqueUseCase(
            PedidoRepository pedidoRepository,
            EstoqueRepository estoqueRepository
    ) {
        this.pedidoRepository = pedidoRepository;
        this.estoqueRepository = estoqueRepository;
    }

    public void executar(UUID pedidoId) {

        Pedido pedido = pedidoRepository
                .buscarPorId(pedidoId)
                .orElseThrow(() ->
                        new IllegalArgumentException(
                                "Pedido não encontrado"
                        )
                );

        for (ItemPedido item : pedido.getItens()) {

            Estoque estoque = estoqueRepository
                    .buscarPorProdutoId(item.getProduto().getId())
                    .orElseThrow(() ->
                            new IllegalArgumentException(
                                    "Estoque não encontrado para o produto "
                                            + item.getProduto().getId()
                            )
                    );

            estoque.reservar(item.getQuantidade());

            estoqueRepository.salvar(estoque);
        }

        pedidoRepository.salvar(pedido);
    }
}