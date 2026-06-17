package org.br.api;

import org.br.application.dto.CriarPedidoDTO;
import org.br.application.dto.PedidoResponseDTO;
import org.br.application.mapper.PedidoMapper;
import org.br.application.usecase.*;
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
    private final ReservarEstoqueUseCase reservarEstoqueUseCase;
    private final ExpedirPedidoUseCase expedirPedidoUseCase;
    private final SepararPedidoUseCase separarPedidoUseCase;

    public PedidoController(
            CriarPedidoUseCase criarPedidoUseCase,
            BuscarPedidoUseCase buscarPedidoUseCase,
            ReservarEstoqueUseCase reservarEstoqueUseCase,
            ExpedirPedidoUseCase expedirPedidoUseCase,
            SepararPedidoUseCase separarPedidoUseCase
    ) {
        this.criarPedidoUseCase = criarPedidoUseCase;
        this.buscarPedidoUseCase = buscarPedidoUseCase;
        this.reservarEstoqueUseCase = reservarEstoqueUseCase;
        this.expedirPedidoUseCase = expedirPedidoUseCase;
        this.separarPedidoUseCase = separarPedidoUseCase;
    }

    @PostMapping
    public ResponseEntity<PedidoResponseDTO> criarPedido(
            @RequestBody CriarPedidoDTO dto
    ) {

        Pedido pedido =
                criarPedidoUseCase.executar(dto);

        PedidoResponseDTO response =
                PedidoMapper.toResponseDTO(pedido);

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

    @PostMapping("/{id}/reservar")
    public ResponseEntity<Void> reservar(
            @PathVariable UUID id
    ) {

        reservarEstoqueUseCase.executar(id);

        return ResponseEntity.ok().build();
    }

    @PostMapping("/{id}/expedir")
    public ResponseEntity<Void> expedirPedido(
            @PathVariable UUID id
    ) {

        expedirPedidoUseCase.executar(id);

        return ResponseEntity.ok().build();
    }

    @PostMapping("/{id}/separar")
    public ResponseEntity<Void> separar(
            @PathVariable UUID id
    ) {

        separarPedidoUseCase.executar(id);

        return ResponseEntity.ok().build();
    }
}
