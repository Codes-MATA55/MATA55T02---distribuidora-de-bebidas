package org.br.domain.estoque;

import java.util.Optional;
import java.util.UUID;

public interface EstoqueRepository {

    void salvar(Estoque estoque);

    Optional<Estoque> buscarPorProdutoId(UUID produtoId);

}
