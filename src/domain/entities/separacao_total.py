from datetime import date
from typing import List

from domain.entities.lote import Lote
from domain.entities.pedido import Pedido


class SeparacaoTotal:
    """Serviço de domínio para separação total com estratégia FEFO."""

    def executar(self, pedido: Pedido, lotes_disponiveis: List[Lote], data_referencia: date = None) -> None:
        if data_referencia is None:
            data_referencia = date.today()

        if pedido.status != "EM PROCESSAMENTO":
            raise ValueError(
                f"Não é possível separar o pedido {pedido.id}. "
                f"Status atual inválido: {pedido.status}"
            )

        for item in pedido.itens:
            produto = getattr(item, "produto", None)
            quantidade_necessaria = getattr(item, "quantidade", 0)

            if not produto:
                raise ValueError("Item de pedido não possui um produto associado.")

            lotes_do_produto = [
                lote for lote in lotes_disponiveis
                if lote.produto.codigo_barras == produto.codigo_barras
                and not lote.esta_vencido(data_referencia)
            ]

            total_disponivel = sum(lote.quantidade_atual for lote in lotes_do_produto)

            if total_disponivel < quantidade_necessaria:
                raise ValueError(
                    f"Separação inválida para o produto '{produto.nome}'. "
                    f"Necessário: {quantidade_necessaria}, disponível em lotes válidos: {total_disponivel}"
                )

        for item in pedido.itens:
            produto = getattr(item, "produto", None)
            quantidade_restante = getattr(item, "quantidade", 0)

            lotes_do_produto = sorted(
                [
                    lote for lote in lotes_disponiveis
                    if lote.produto.codigo_barras == produto.codigo_barras
                    and not lote.esta_vencido(data_referencia)
                ],
                key=lambda lote: lote.data_validade,
            )

            for lote in lotes_do_produto:
                if quantidade_restante <= 0:
                    break

                quantidade_a_retirar = min(lote.quantidade_atual, quantidade_restante)
                lote.consumir_quantidade(quantidade_a_retirar)
                quantidade_restante -= quantidade_a_retirar

            produto.baixar_estoque(getattr(item, "quantidade", 0))

        pedido.atualizar_status("SEPARADO")
