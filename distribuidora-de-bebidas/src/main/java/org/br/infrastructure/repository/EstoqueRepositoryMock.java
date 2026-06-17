package org.br.infrastructure.repository;

import org.br.domain.estoque.Estoque;
import org.br.domain.estoque.EstoqueRepository;
import org.br.domain.estoque.Produto;
import org.springframework.stereotype.Repository;

import java.math.BigDecimal;
import java.util.HashMap;
import java.util.Map;
import java.util.Optional;
import java.util.UUID;

@Repository
public class EstoqueRepositoryMock implements EstoqueRepository {

    private final Map<UUID, Estoque> estoques = new HashMap<>();

    public EstoqueRepositoryMock() {

        Produto coca = new Produto(
                UUID.randomUUID(),
                "Coca-Cola 2L",
                new BigDecimal("12.50")
        );

        Produto pepsi = new Produto(
                UUID.randomUUID(),
                "Pepsi 2L",
                new BigDecimal("11.90")
        );

        Produto guarana = new Produto(
                UUID.randomUUID(),
                "Guaraná Antarctica 2L",
                new BigDecimal("10.50")
        );

        estoques.put(
                coca.getId(),
                new Estoque(coca, 100)
        );

        estoques.put(
                pepsi.getId(),
                new Estoque(pepsi, 50)
        );

        estoques.put(
                guarana.getId(),
                new Estoque(guarana, 75)
        );
    }

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
