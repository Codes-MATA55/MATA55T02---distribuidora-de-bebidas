package org.br.application.usecase;

import org.br.application.dto.CriarPedidoDTO;
import org.br.domain.pedido.ItemPedido;
import org.br.domain.pedido.Pedido;
import org.br.domain.pedido.PedidoRepository;
import org.springframework.stereotype.Service;

import java.util.List;

@Service
public class CriarPedidoUseCase {

    private final PedidoRepository repository;

    public CriarPedidoUseCase(
            PedidoRepository repository
    ) {
        this.repository = repository;
    }

    public Pedido executar(
            CriarPedidoDTO itens
    ) {

        Pedido pedido = new Pedido((List<ItemPedido>) itens);

        repository.salvar(pedido);

        return pedido;
    }
}
