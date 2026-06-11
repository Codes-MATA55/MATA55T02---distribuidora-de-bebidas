package org.br.domain.estoque;

import java.time.LocalDateTime;
import java.util.UUID;

public class MovimentacaoEstoque {

    private UUID id;

    private Produto produto;

   // private TipoMovimentacao tipo;

    private int quantidade;

    private LocalDateTime data;
}
