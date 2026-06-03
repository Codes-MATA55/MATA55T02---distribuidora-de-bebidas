package org.br.application.usecase;

import org.br.application.dto.PedidoResponseDTO;
import org.br.domain.pedido.Pedido;
import org.br.domain.pedido.PedidoRepository;
import org.springframework.stereotype.Service;

import java.util.UUID;

@Service
public class BuscarPedidoUseCase {

    private final PedidoRepository pedidoRepository;

    public BuscarPedidoUseCase(PedidoRepository pedidoRepository) {
        this.pedidoRepository = pedidoRepository;
    }

    public PedidoResponseDTO executar(UUID id) {

        Pedido pedido = pedidoRepository
                .buscarPorId(id)
                .orElseThrow(() ->
                        new IllegalArgumentException(
                                "Pedido não encontrado: " + id
                        )
                );

        return new PedidoResponseDTO(
                pedido.getId(),
                pedido.getStatus()
        );
    }
}
