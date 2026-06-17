package org.br.infrastructure.repository;

import org.br.domain.estoque.Produto;
import org.br.domain.pedido.ItemPedido;
import org.br.domain.pedido.Pedido;
import org.br.domain.pedido.PedidoRepository;
import org.springframework.stereotype.Repository;

import java.math.BigDecimal;
import java.util.*;

@Repository
public class PedidoRepositoryMock
        implements PedidoRepository {

    private final Map<UUID, Pedido> pedidos =
            new HashMap<>();

    public PedidoRepositoryMock() {

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

        List<ItemPedido> itens = List.of(
                new ItemPedido(coca.getId(), 2),
                new ItemPedido(pepsi.getId(), 1)
        );

        Pedido pedido = new Pedido(itens);

        pedidos.put(
                pedido.getId(),
                pedido
        );
    }

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