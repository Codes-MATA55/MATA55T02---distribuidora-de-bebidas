package org.br.domain.pedido;

import java.util.Optional;
import java.util.UUID;

public interface PedidoRepository {

    void salvar(Pedido pedido);

    Optional<Pedido> buscarPorId(UUID id);

}