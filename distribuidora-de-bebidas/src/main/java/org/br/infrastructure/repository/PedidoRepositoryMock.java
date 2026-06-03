package org.br.infrastructure.repository;

import org.br.domain.pedido.Pedido;
import org.br.domain.pedido.PedidoRepository;
import org.springframework.stereotype.Repository;

import java.util.HashMap;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;

@Repository
public class PedidoRepositoryMock
        implements PedidoRepository {

    private final Map<UUID, Pedido> pedidos =
            new HashMap<>();

    @Override
    public void salvar(Pedido pedido) {
        pedidos.put(
                pedido.getId(),
                pedido
        );
    }

    @Override
    public Optional<Pedido> buscarPorId(UUID id) {
        return Optional.ofNullable(
                pedidos.get(id)
        );
    }
}
