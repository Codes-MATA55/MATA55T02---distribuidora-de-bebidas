import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.bebida.cerveja import Cerveja  # noqa: E402
from src.bebida.refrigerante import Refrigerante  # noqa: E402
from src.bebida.suco import Suco  # noqa: E402
from src.estoque.estoque import Estoque  # noqa: E402
from src.pedido.pedido import Pedido  # noqa: E402
from src.pedido.item_pedido import ItemPedido  # noqa: E402
from src.separacao.fifo import FIFOSeparacao  # noqa: E402
from src.expedicao.regras import ValidadorExpedicao  # noqa: E402
from src.usuario.operador import Operador, Supervisor, Gerente  # noqa: E402
from src.observadores.observer import EventBus  # noqa: E402
from src.observadores.logger import (  # noqa: E402
    MonitoramentoObserver,
    AtualizacaoEstoqueObserver,
)
from src.exceptions.regras_negocio import (  # noqa: E402
    TransicaoDeEstadoInvalidaException,
    RegraDeExpedicaoVioladaException,
)


def separador(titulo: str) -> None:
    print(f"\n{'='*60}")
    print(f"  {titulo}")
    print(f"{'='*60}")


def subsecao(titulo: str) -> None:
    print(f"\n--- {titulo} ---")


def criar_catalogo() -> tuple:
    separador("1. Criando Catalogo (Hierarquia de bebidas)")

    cerveja = Cerveja(
        nome="Original",
        volume_ml=350,
        preco_unitario=4.50,
        tipo="Original",
    )
    refrigerante = Refrigerante(
        nome="Coca Cola Zero",
        volume_ml=350,
        preco_unitario=3.20,
        sabor="Coca",
        is_diet=False,
    )
    suco = Suco(
        nome="Suco de Laranja",
        volume_ml=1000,
        preco_unitario=8.90,
        fruta="Laranja",
    )

    for bebida in [cerveja, refrigerante, suco]:
        print(f"  {bebida.descricao_completa()}")

    return cerveja, refrigerante, suco


def abastecer_estoque(cerveja, refrigerante, suco) -> Estoque:
    separador("2. Gerenciador de Estoque")

    estoque = Estoque()
    for bebida in [cerveja, refrigerante, suco]:
        estoque.registrar_produto(bebida)

    subsecao("Entradas de estoque")
    entradas = [
        (cerveja.id, 50_000, "Lote diario de cervejas"),
        (refrigerante.id, 30_000, "Lote diario de refrigerantes"),
        (suco.id, 100_000, "Lote diario de sucos"),
    ]
    for pid, qtd, motivo in entradas:
        estoque.entrada(pid, qtd, motivo)
        prod = estoque.produto(pid)
        print(f"{prod.nome}: +{qtd:,} unidades")

    subsecao("Saldos atuais")
    for info in estoque.resumo().values():
        print(
            f"{info['nome']} ({info['categoria']}): "
            f"{info['saldo']:,} un."
        )

    return estoque


def configurar_observers(estoque: Estoque) -> tuple:
    separador("3. Config event bus")

    event_bus = EventBus()
    monitoramento = MonitoramentoObserver()

    todos_eventos = [
        "PEDIDO_SEPARADO",
        "PEDIDO_EM_EXPEDICAO",
        "PEDIDO_ENTREGUE",
        "PEDIDO_CANCELADO",
    ]
    event_bus.assinar_todos(todos_eventos, monitoramento)
    event_bus.assinar(
        "PEDIDO_ENTREGUE", AtualizacaoEstoqueObserver(estoque)
    )
    print("Observer registrados")

    return event_bus, monitoramento


def demonstrar_fluxo_completo(
    cerveja, refrigerante, suco, estoque, event_bus
) -> None:
    separador("4. Fluxo de pedidos")

    operador = Operador(nome="Alessandro Libertador")
    print(f"Operador: {operador}")

    pedido = Pedido(cliente="Mercado Ufba", event_bus=event_bus)
    pedido.adicionar_item(ItemPedido(cerveja.id, cerveja, 500))
    pedido.adicionar_item(ItemPedido(refrigerante.id, refrigerante, 300))
    pedido.adicionar_item(ItemPedido(suco.id, suco, 1_000))

    print(f"   Historico de estados: {pedido.historico_estados}")

    subsecao("Separacao")
    FIFOSeparacao().separar(pedido, estoque)

    subsecao("Envio")
    ValidadorExpedicao().validar(pedido, estoque)
    print("Todas as regras de envio aprovadas.")
    pedido.iniciar_expedicao()
    print(f"Estado: {pedido.estado_atual}")

    subsecao("Confirmacao de Entrega")
    pedido.confirmar_entrega()
    print(f"Estado final: {pedido.estado_atual}")
    print(f"Historico completo: {pedido.historico_estados}")
    print(f"Valor total: R$ {pedido.valor_total:.2f}")


def demonstrar_cancelamento(cerveja, event_bus) -> None:
    separador("5. Cancelamento do Pedido")

    supervisor = Supervisor(nome="Caio Porto")
    pode = supervisor.pode_cancelar_pedido()
    print(f"Supervisor: {supervisor} | Pode cancelar: {pode}")

    pedido = Pedido(cliente="Bar do Lucas", event_bus=event_bus)
    pedido.adicionar_item(ItemPedido(cerveja.id, cerveja, 50))
    print(f"\n{pedido}")
    pedido.cancelar()
    print(f"Estado: {pedido.estado_atual}")


def demonstrar_transicao_invalida(cerveja) -> None:
    separador("6. Teste invalido")

    pedido = Pedido(cliente="Teste Invalido")
    pedido.adicionar_item(ItemPedido(cerveja.id, cerveja, 10))
    try:
        pedido.confirmar_entrega()
    except TransicaoDeEstadoInvalidaException as e:
        print(f"Bloqueado corretamente: {e}")


def demonstrar_expedicao_bloqueada(cerveja, estoque) -> None:
    separador("7. Envio bloqueado")

    pedido = Pedido(cliente="Cliente Sem Separar")
    pedido.adicionar_item(ItemPedido(cerveja.id, cerveja, 10))
    try:
        ValidadorExpedicao().validar(pedido, estoque)
    except RegraDeExpedicaoVioladaException as e:
        print(f"Bloqueado corretamente:\n{e}")


def demonstrar_usuarios() -> tuple:
    separador("8. Hierarquia de usuarios")

    operador = Operador(nome="Alessandro Libertador")
    supervisor = Supervisor(nome="Caio Porto")
    gerente = Gerente(nome="Jose Guilherme")
    usuarios = [operador, supervisor, gerente]

    cabecalho = (
        f"{'Usuario':<20} {'Nivel':<12} "
        f"{'Cancelar':<10} {'Relatorio':<12} {'Estoque'}"
    )
    print(cabecalho)
    print("-" * 65)
    for u in usuarios:
        cancelar = "Sim" if u.pode_cancelar_pedido() else "Nao"
        relatorio = "Sim" if u.pode_gerar_relatorio() else "Nao"
        estoque_perm = "Sim" if u.pode_alterar_estoque() else "Nao"
        print(
            f"{u.nome:<20} {u.nivel_acesso.name:<12} "
            f"{cancelar:<10} {relatorio:<12} {estoque_perm}"
        )

    return operador, supervisor, gerente


def exibir_metricas(monitoramento, estoque) -> None:
    separador("9. Metricas")

    monitoramento.exibir_metricas()

    print("\nSaldos finais")
    for info in estoque.resumo().values():
        print(f"  {info['nome']}: {info['saldo']:,} un.")


def main() -> None:
    print("\nDistribuidora de bebidas POO")

    cerveja, refrigerante, suco = criar_catalogo()
    estoque = abastecer_estoque(cerveja, refrigerante, suco)
    event_bus, monitoramento = configurar_observers(estoque)

    demonstrar_fluxo_completo(cerveja, refrigerante, suco, estoque, event_bus)
    demonstrar_cancelamento(cerveja, event_bus)
    demonstrar_transicao_invalida(cerveja)
    demonstrar_expedicao_bloqueada(cerveja, estoque)
    demonstrar_usuarios()
    exibir_metricas(monitoramento, estoque)


if __name__ == "__main__":
    main()
