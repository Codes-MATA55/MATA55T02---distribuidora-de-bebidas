package org.br.infrastructure.repository;

import org.br.domain.estoque.Estoque;
import org.br.domain.estoque.EstoqueRepository;
import org.springframework.stereotype.Repository;

import java.util.HashMap;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;

@Repository
public class EstoqueRepositoryMock implements EstoqueRepository {

    private final Map<UUID, Estoque> estoques = new HashMap<>();

    @Override
    public void salvar(Estoque estoque) {
        estoques.put(
                estoque.getProduto().getId(),
                estoque
        );
    }

    @Override
    public Optional<Estoque> buscarPorProdutoId(UUID produtoId) {
        return Optional.ofNullable(
                estoques.get(produtoId)
        );
    }
}
