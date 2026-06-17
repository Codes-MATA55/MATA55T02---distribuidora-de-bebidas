package org.br.application.usecase;

import org.br.domain.estoque.Estoque;
import org.br.domain.estoque.EstoqueRepository;
import org.br.domain.pedido.ItemPedido;
import org.br.domain.pedido.Pedido;
import org.br.domain.pedido.PedidoRepository;
import org.br.domain.pedido.StatusPedido;
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

        if (pedido.getStatus() != StatusPedido.CRIADO
                && pedido.getStatus() != StatusPedido.AGUARDANDO_ESTOQUE) {

            throw new IllegalStateException(
                    "Pedido já foi reservado ou não pode ser reservado"
            );
        }

        for (ItemPedido item : pedido.getItens()) {

            Estoque estoque = estoqueRepository
                    .buscarPorProdutoId(item.getProdutoId())
                    .orElseThrow(() ->
                            new IllegalArgumentException(
                                    "Estoque não encontrado para o produto "
                                            + item.getProdutoId()
                            )
                    );

            estoque.reservar(item.getQuantidade());

            estoqueRepository.salvar(estoque);
        }

        pedido.iniciarSeparacao();

        pedidoRepository.salvar(pedido);
    }
}