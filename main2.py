"""
Distribuidora de Bebidas POO
"""

from src.bebida.cerveja import Cerveja
from src.bebida.refrigerante import Refrigerante
from src.bebida.suco import Suco

from src.estoque.estoque import Estoque

from src.pedido.pedido import Pedido
from src.pedido.item_pedido import ItemPedido

from src.separacao.fifo import FIFOSeparacao

from src.expedicao.regras import ValidadorExpedicao

from src.usuario.operador import Operador, Supervisor, Gerente

from src.observadores.observer import EventBus
from src.observadores.logger import LoggerObserver, MonitoramentoObserver, AtualizacaoEstoqueObserver

from src.exceptions.regras_negocio import (
    TransicaoDeEstadoInvalidaException,
    RegraDeExpedicaoVioladaException,
)


def separador(titulo: str) -> None:
    print()
    print(f"  {titulo}")
    


def subsecao(titulo: str) -> None:
    print(f"\n--- {titulo} ---")


def main() -> None:
    print("\nDISTRIBUIDORA DE BEBIDAS")
    print("     Demonstração de POO, DDD e Design Patterns\n")


    # 1. Config event bus

    separador("")

    event_bus = EventBus()

    monitoramento = MonitoramentoObserver()

    todos_eventos = [
        "PEDIDO_SEPARADO",
        "PEDIDO_EM_EXPEDICAO",
        "PEDIDO_ENTREGUE",
        "PEDIDO_CANCELADO",
    ]


    # 2. Catálogo de Bebidas

    separador("1. Catálogo de Bebidas")

    cerveja_original = Cerveja(
        nome="Original",
        volume_ml=350,
        preco_unitario=4.50,
        tipo="Original",
    )
    refrigerante_coca = Refrigerante(
        nome="Coca Zero",
        volume_ml=350,
        preco_unitario=3.20,
        sabor="Coca",
        is_diet=True,
    )
    suco_laranja = Suco(
        nome="Suco de Laranja",
        volume_ml=1000,
        preco_unitario=8.90,
        fruta="Laranja",
        percentual_polpa=100.0,
    )

    for bebida in [cerveja_original, refrigerante_coca, suco_laranja]:
        print(f"   {bebida.descricao_completa()}")


    # 3. Estoque

    separador("2. GERENCIANDO ESTOQUE")

    estoque = Estoque()

    # Registra produtos no catálogo
    for bebida in [cerveja_original, refrigerante_coca, suco_laranja]:
        estoque.registrar_produto(bebida)

    # Conecta observer de estoque ao event bus após criação do estoque
    obs_estoque = AtualizacaoEstoqueObserver(estoque)
    event_bus.assinar("PEDIDO_ENTREGUE", obs_estoque)

    # Entrada de estoque (simula escala da distribuidora)
    subsecao("Entradas de estoque")
    entradas = [
        (cerveja_original.id, 50_000, "Lote diário de cervejas"),
        (refrigerante_coca.id, 30_000, "Lote diário de refrigerantes"),
        (suco_laranja.id, 100_000, "Lote diário de sucos"),
    ]
    for pid, qtd, motivo in entradas:
        estoque.entrada(pid, qtd, motivo)
        prod = estoque.produto(pid)
        print(f" {prod.nome}: +{qtd:,} unidades")

    subsecao("Qtd atuais")
    for pid, info in estoque.resumo().items():
        print(f"  {info['nome']} ({info['categoria']}): {info['saldo']:,} un.")

    # 4. Fluxo do pedido

    separador("3. Fluxo do pedido")

    operador = Operador(nome="Alessandro Jose Lucas Luan")
    print(f" Operador: {operador}")

    # Cria pedido
    pedido = Pedido(cliente="Mercado UFBA", event_bus=event_bus)
    pedido.adicionar_item(ItemPedido(cerveja_original.id, cerveja_original, 500))
    pedido.adicionar_item(ItemPedido(refrigerante_coca.id, refrigerante_coca, 300))
    pedido.adicionar_item(ItemPedido(suco_laranja.id, suco_laranja, 1_000))

    print(f"\n{pedido}")
    print(f"Status: {pedido.historico_estados}")

    # Separação via Strategy FIFO
    subsecao("Separação (Strategy: FIFO)")
    estrategia_fifo = FIFOSeparacao()
    estrategia_fifo.separar(pedido, estoque)
    print(f"\nEstado após separação: {pedido.estado_atual}")
    print(f"Histórico: {pedido.historico_estados}")

    # Validação + Expedição via Specification Pattern
    subsecao("Expedição (Specification Pattern)")
    validador = ValidadorExpedicao()
    validador.validar(pedido, estoque)
    print("Todas as regras de expedição aprovadas.")
    pedido.iniciar_expedicao()
    print(f"Estado: {pedido.estado_atual}")

    # Entrega
    subsecao("Confirmação de Entrega")
    pedido.confirmar_entrega()
    print(f"Estado final: {pedido.estado_atual}")
    print(f"Histórico completo: {pedido.historico_estados}")
    print(f"Valor total: R$ {pedido.valor_total:.2f}")


    # 5. DEMONSTRAÇÃO DE CANCELAMENTO

    separador("4. Cancelamento")

    supervisor = Supervisor(nome="Caio Porto")
    print(f"Supervisor: {supervisor} | Pode cancelar: {supervisor.pode_cancelar_pedido()}")

    pedido_cancelado = Pedido(cliente="Bar da Ufba", event_bus=event_bus)
    pedido_cancelado.adicionar_item(ItemPedido(cerveja_original.id, cerveja_original, 50))
    print(f"\n{pedido_cancelado}")
    pedido_cancelado.cancelar()
    print(f"Estado: {pedido_cancelado.estado_atual}")


    # 6. Transição Inválida

    separador("5. Transição inválida")

    pedido_invalido = Pedido(cliente="Teste Inválido")
    pedido_invalido.adicionar_item(ItemPedido(cerveja_original.id, cerveja_original, 10))
    try:
        pedido_invalido.confirmar_entrega()  # Inválido: Criado → Entregue
    except TransicaoDeEstadoInvalidaException as e:
        print(f"BLOQUEADO corretamente: {e}")


    # 7. Bloqueado

    separador("6. Bloqueado")

    pedido_sem_separar = Pedido(cliente="Cliente Sem Separar")
    pedido_sem_separar.adicionar_item(ItemPedido(cerveja_original.id, cerveja_original, 10))
    try:
        validador.validar(pedido_sem_separar, estoque)
    except RegraDeExpedicaoVioladaException as e:
        print(f"Bloqueado corretamente:\n{e}")


    # 8. Permissão

    separador("7. Permissões")

    gerente = Gerente(nome="Gilberto")
    usuarios = [operador, supervisor, gerente]

    print(f"{'Usuário':<20} {'Nível':<12} {'Cancelar':<10} {'Relatório':<12} {'Estoque'}")
    print("-" * 65)
    for u in usuarios:
        print(
            f"{u.nome:<20} {u.nivel_acesso.name:<12} "
            f"{'Sim' if u.pode_cancelar_pedido() else 'Não':<10} "
            f"{'Sim' if u.pode_gerar_relatorio() else 'Não':<12} "
            f"{'Sim' if u.pode_alterar_estoque() else 'Não'}"
        )


    # 9. Métricas

    separador("8. Métricas")

    monitoramento.exibir_metricas()

    print("\nSaldo final:")
    for pid, info in estoque.resumo().items():
        print(f"  {info['nome']}: {info['saldo']:,} un.")



if __name__ == "__main__":
    main()
