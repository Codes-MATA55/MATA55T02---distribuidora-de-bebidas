from typing import List
from datetime import date
from domain.entities.pedido import Pedido
from domain.entities.lote import Lote


class SeparacaoTotal:

    # Serviço de Domínio responsável por executar a separação total de um pedido
    # utilizando a estratégia FEFO (First Expired, First Out) e garantindo a atomicidade
    # da baixa de estoque.
    

    def executar(self, pedido: Pedido, lotes_disponiveis: List[Lote], data_referencia: date = None) -> None:
        if data_referencia is None:
            data_referencia = date.today()

        # Invariante de Estado: O pedido precisa estar em processamento para ser separado
        if pedido.status != "EM PROCESSAMENTO":
            raise ValueError(
                f"Não é possível separar o pedido {pedido.id}. "
                f"Status atual inválido: {pedido.status}"
            )

        # 1. PRÉ-VALIDAÇÃO (Garantia de Bloqueio de Separação Inválida)
        # Varre todo o pedido antes de alterar qualquer dado para garantir consistência atômica
        for item in pedido.produtos:
            # Tratamento dinâmico para obter o produto independente da modelagem do ItemPedido
            produto = getattr(item, "produto", None)
            quantidade_necessaria = getattr(item, "quantidade", 0)

            if not produto:
                raise ValueError("Item de pedido não possui um produto associado.")

            # Filtra apenas lotes válidos e não vencidos para este produto específico
            lotes_do_produto = [
                lote for lote in lotes_disponiveis
                if lote.produto.codbarras == produto.codbarras and not lote.esta_vencido(data_referencia)
            ]

            total_disponivel = sum(lote.quantidade_atual for lote in lotes_do_produto)

            # Regra de negócio: Se faltar estoque para um único item, a separação inteira é abortada
            if total_disponivel < quantidade_necessaria:
                raise ValueError(
                    f"Separação inválida para o produto '{produto.nome}'. "
                    f"Necessário: {quantidade_necessaria}, Disponível em lotes válidos: {total_disponivel}"
                )

        # 2. EXECUÇÃO DA SEPARAÇÃO (Estratégia FEFO)
        # Se passou pela validação prévia, podemos realizar os consumos com segurança
        for item in pedido.produtos:
            produto = getattr(item, "produto", None)
            quantidade_restante = getattr(item, "quantidade", 0)

            # Ordena os lotes ativos colocando os que vencem mais cedo primeiro (FEFO)
            lotes_do_produto = sorted(
                [
                    lote for lote in lotes_disponiveis
                    if lote.produto.codbarras == produto.codbarras and not lote.esta_vencido(data_referencia)
                ],
                key=lambda x: x.data_validade
            )

            for lote in lotes_do_produto:
                if quantidade_restante <= 0:
                    break

                quantidade_a_retirar = min(lote.quantidade_atual, quantidade_restante)
                lote.consumir_quantidade(quantidade_a_retirar)
                quantidade_restante -= quantidade_a_retirar

            # Sincroniza e atualiza o saldo consolidado na entidade legada Produto da equipe
            produto.baixar_estoque(getattr(item, "quantidade", 0))

        # 3. ATUALIZAÇÃO DO STATUS DO PEDIDO (Fronteira de transição para a AF3)
        pedido.atualizar_status("SEPARADO")