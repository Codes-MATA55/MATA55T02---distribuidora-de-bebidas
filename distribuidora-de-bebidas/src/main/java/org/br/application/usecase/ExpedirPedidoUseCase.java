package org.br.application.usecase;

import org.br.domain.expedicao.Expedicao;
import org.br.domain.expedicao.ExpedicaoRepository;
import org.br.domain.pedido.Pedido;
import org.br.domain.pedido.PedidoRepository;
import org.springframework.stereotype.Service;

import java.util.UUID;

@Service
public class ExpedirPedidoUseCase {

    private final PedidoRepository pedidoRepository;
    private final ExpedicaoRepository expedicaoRepository;

    public ExpedirPedidoUseCase(
            PedidoRepository pedidoRepository,
            ExpedicaoRepository expedicaoRepository
    ) {
        this.pedidoRepository = pedidoRepository;
        this.expedicaoRepository = expedicaoRepository;
    }

    public void executar(UUID pedidoId) {
        Pedido pedido = pedidoRepository
                .buscarPorId(pedidoId)
                .orElseThrow(() ->
                        new IllegalArgumentException("Pedido não encontrado")
                );

        pedido.expedir();

        Expedicao expedicao = new Expedicao(pedido);

        pedidoRepository.salvar(pedido);
        expedicaoRepository.salvar(expedicao);
    }
}
