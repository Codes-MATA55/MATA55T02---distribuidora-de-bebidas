package org.br.application.usecase;

import org.br.application.dto.CriarPedidoDTO;
import org.br.application.mapper.PedidoMapper;
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
            CriarPedidoDTO dto
    ) {

        Pedido pedido =
                PedidoMapper.toEntity(dto);

        repository.salvar(pedido);

        return pedido;
    }
}
