package org.br.application.dto;

import lombok.Getter;
import org.br.domain.pedido.StatusPedido;

import java.util.UUID;

@Getter
public class PedidoResponseDTO {

    private UUID id;
    private StatusPedido status;

    public PedidoResponseDTO(UUID id, StatusPedido status) {
        this.id = id;
        this.status = status;
    }

}

