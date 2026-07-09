package org.br.domain.expedicao;

import org.br.domain.identity.Permissao;
import org.br.domain.identity.Usuario;
import org.br.domain.pedido.Pedido;
import org.br.domain.pedido.StatusPedido;

import java.util.List;
import java.util.UUID;

public class OrdemExpedicao {

    private final UUID id;
    private final List<Pedido> pedidos;
    private boolean liberada;

    public OrdemExpedicao(List<Pedido> pedidos) {

        if (pedidos == null || pedidos.isEmpty()) {
            throw new IllegalArgumentException(
                    "Ordem de expedição deve possuir pedidos"
            );
        }

        if (pedidos.stream().anyMatch(pedido -> pedido == null)) {
            throw new IllegalArgumentException(
                    "Pedido da ordem de expedição é obrigatório"
            );
        }

        this.id = UUID.randomUUID();
        this.pedidos = List.copyOf(pedidos);
        this.liberada = false;
    }

    public void liberar(Usuario usuario) {

        if (usuario == null || !usuario.pode(Permissao.LIBERAR_EXPEDICAO)) {
            throw new IllegalStateException(
                    "Usuário não pode liberar expedição"
            );
        }

        if (pedidos.stream().anyMatch(this::naoEstaProntoParaExpedicao)) {
            throw new IllegalStateException(
                    "Ordem possui pedido não separado"
            );
        }

        this.liberada = true;
    }

    private boolean naoEstaProntoParaExpedicao(Pedido pedido) {
        return pedido.getStatus() != StatusPedido.SEPARADO
                && pedido.getStatus() != StatusPedido.EM_EXPEDICAO
                && pedido.getStatus() != StatusPedido.EXPEDIDO;
    }

    public UUID getId() {
        return id;
    }

    public List<Pedido> getPedidos() {
        return pedidos;
    }

    public boolean isLiberada() {
        return liberada;
    }
}
