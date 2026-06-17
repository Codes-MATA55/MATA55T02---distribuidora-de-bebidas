package org.br.domain.expedicao;

import org.br.domain.pedido.Pedido;
import org.br.domain.pedido.StatusPedido;

import java.time.LocalDateTime;
import java.util.UUID;

public class Expedicao {

    private final UUID id;
    private final UUID pedidoId;
    private final LocalDateTime dataExpedicao;

    public Expedicao(Pedido pedido) {
        if (pedido == null) {
            throw new IllegalArgumentException("Pedido é obrigatório");
        }

        if (pedido.getStatus() != StatusPedido.EXPEDIDO) {
            throw new IllegalStateException(
                    "Expedição só pode ser registrada para pedido expedido"
            );
        }

        this.id = UUID.randomUUID();
        this.pedidoId = pedido.getId();
        this.dataExpedicao = LocalDateTime.now();
    }

    public UUID getId() {
        return id;
    }

    public UUID getPedidoId() {
        return pedidoId;
    }

    public LocalDateTime getDataExpedicao() {
        return dataExpedicao;
    }
}
