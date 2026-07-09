package org.br.domain.identity;

import java.util.EnumSet;
import java.util.Set;

public enum Cargo {

    OPERADOR_ESTOQUE(
            Permissao.REGISTRAR_ESTOQUE
    ),

    SEPARADOR(
            Permissao.SEPARAR_PEDIDO
    ),

    CONFERENTE(
            Permissao.CONFERIR_PEDIDO
    ),

    GERENTE_LOGISTICO(
            Permissao.LIBERAR_EXPEDICAO,
            Permissao.CANCELAR_PEDIDO,
            Permissao.REGISTRAR_ESTOQUE
    );

    private final Set<Permissao> permissoes;

    Cargo(Permissao... permissoes) {
        this.permissoes = EnumSet.noneOf(Permissao.class);
        this.permissoes.addAll(Set.of(permissoes));
    }

    public boolean possui(Permissao permissao) {
        return permissoes.contains(permissao);
    }
}
