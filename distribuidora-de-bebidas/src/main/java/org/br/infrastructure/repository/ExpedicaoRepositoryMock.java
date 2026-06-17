package org.br.infrastructure.repository;

import org.br.domain.expedicao.Expedicao;
import org.br.domain.expedicao.ExpedicaoRepository;
import org.springframework.stereotype.Repository;

import java.util.HashMap;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;

@Repository
public class ExpedicaoRepositoryMock implements ExpedicaoRepository {

    private final Map<UUID, Expedicao> expedicoesPorPedido = new HashMap<>();

    @Override
    public void salvar(Expedicao expedicao) {
        expedicoesPorPedido.put(expedicao.getPedidoId(), expedicao);
    }

    @Override
    public Optional<Expedicao> buscarPorPedidoId(UUID pedidoId) {
        return Optional.ofNullable(expedicoesPorPedido.get(pedidoId));
    }
}
