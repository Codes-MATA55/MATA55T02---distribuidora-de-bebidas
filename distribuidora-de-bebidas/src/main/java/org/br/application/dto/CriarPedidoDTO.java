package org.br.application.dto;

import java.util.List;

public class CriarPedidoDTO {

    private List<ItemPedidoDTO> itens;

    public List<ItemPedidoDTO> getItens() {
        return itens;
    }

    public void setItens(List<ItemPedidoDTO> itens) {
        this.itens = itens;
    }
}
