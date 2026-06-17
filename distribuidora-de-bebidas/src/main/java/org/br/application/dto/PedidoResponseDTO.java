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

    public UUID getId() {
        return id;
    }

    public void setId(UUID id) {
        this.id = id;
    }

    public StatusPedido getStatus() {
        return status;
    }

    public void setStatus(StatusPedido status) {
        this.status = status;
    }
}

