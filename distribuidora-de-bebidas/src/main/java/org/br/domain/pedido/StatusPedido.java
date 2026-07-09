package org.br.domain.pedido;

public enum StatusPedido {
    CRIADO,
    AGUARDANDO_ESTOQUE,
    EM_SEPARACAO,
    SEPARADO,
    EM_EXPEDICAO,
    EXPEDIDO,
    CANCELADO
}
