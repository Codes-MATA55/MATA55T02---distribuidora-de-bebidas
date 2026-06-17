package org.br.domain.expedicao;

import java.util.Optional;
import java.util.UUID;

public interface ExpedicaoRepository {

    void salvar(Expedicao expedicao);

    Optional<Expedicao> buscarPorPedidoId(UUID pedidoId);
}
