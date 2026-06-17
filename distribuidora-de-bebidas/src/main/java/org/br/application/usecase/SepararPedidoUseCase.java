package org.br.application.usecase;

import org.br.domain.pedido.Pedido;
import org.br.domain.pedido.PedidoRepository;
import org.springframework.stereotype.Service;

import java.util.UUID;

@Service
public class SepararPedidoUseCase {

    private final PedidoRepository pedidoRepository;

    public SepararPedidoUseCase(
            PedidoRepository pedidoRepository
    ) {
        this.pedidoRepository = pedidoRepository;
    }

    public void executar(UUID pedidoId) {

        Pedido pedido = pedidoRepository
                .buscarPorId(pedidoId)
                .orElseThrow(() ->
                        new IllegalArgumentException(
                                "Pedido não encontrado"
                        )
                );

        pedido.separar();

        pedidoRepository.salvar(pedido);
    }
}
