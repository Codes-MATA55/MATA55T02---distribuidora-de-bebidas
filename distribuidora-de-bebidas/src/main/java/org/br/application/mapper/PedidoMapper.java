package org.br.application.mapper;

import org.br.application.dto.CriarPedidoDTO;
import org.br.application.dto.PedidoResponseDTO;
import org.br.domain.pedido.ItemPedido;
import org.br.domain.pedido.Pedido;

import java.util.List;

public class PedidoMapper {

    public static Pedido toEntity(CriarPedidoDTO dto) {

        List<ItemPedido> itens = dto.getItens()
                .stream()
                .map(item ->
                        new ItemPedido(
                                item.getProdutoId(),
                                item.getQuantidade()
                        )
                )
                .toList();

        return new Pedido(itens);
    }

    public static PedidoResponseDTO toResponseDTO(
            Pedido pedido
    ) {
        return new PedidoResponseDTO(
                pedido.getId(),
                pedido.getStatus()
        );
    }
}