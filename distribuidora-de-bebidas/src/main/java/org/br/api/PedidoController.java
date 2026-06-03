package org.br.api;

import org.br.application.dto.CriarPedidoDTO;
import org.br.application.dto.PedidoResponseDTO;
import org.br.application.usecase.BuscarPedidoUseCase;
import org.br.application.usecase.CriarPedidoUseCase;
import org.br.domain.pedido.Pedido;
import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.UUID;

@RestController
@RequestMapping("/pedidos")
public class PedidoController {

    private final CriarPedidoUseCase criarPedidoUseCase;
    private final BuscarPedidoUseCase buscarPedidoUseCase;

    public PedidoController(
            CriarPedidoUseCase criarPedidoUseCase,
            BuscarPedidoUseCase buscarPedidoUseCase
    ) {
        this.criarPedidoUseCase = criarPedidoUseCase;
        this.buscarPedidoUseCase = buscarPedidoUseCase;
    }

    @PostMapping
    public ResponseEntity<Pedido> criarPedido(
            @RequestBody CriarPedidoDTO dto
    ) {

        Pedido response =
                criarPedidoUseCase.executar(dto);

        return ResponseEntity
                .status(HttpStatus.CREATED)
                .body(response);
    }

    @GetMapping("/{id}")
    public ResponseEntity<PedidoResponseDTO> buscarPorId(
            @PathVariable UUID id
    ) {

        PedidoResponseDTO response =
                buscarPedidoUseCase.executar(id);

        return ResponseEntity.ok(response);
    }
}
