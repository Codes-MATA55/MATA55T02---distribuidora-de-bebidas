from .observer import Observer, Evento
from ..estoque.estoque import Estoque


class LoggerObserver(Observer):

    def __init__(self) -> None:
        self._logs: list[str] = []

    def notificar(self, evento: Evento) -> None:
        entrada = f"[{evento.timestamp:%Y-%m-%d %H:%M:%S}] {evento.tipo}: {evento.dados}"
        self._logs.append(entrada)

    def obter_logs(self) -> list[str]:
        return list(self._logs)


class MonitoramentoObserver(Observer):

    def __init__(self) -> None:
        self._contadores: dict[str, int] = {}

    def notificar(self, evento: Evento) -> None:
        self._contadores[evento.tipo] = self._contadores.get(evento.tipo, 0) + 1

    def metricas(self) -> dict[str, int]:
        return dict(self._contadores)

    def exibir_metricas(self) -> None:
        pass


class AtualizacaoEstoqueObserver(Observer):

    def __init__(self, estoque: Estoque) -> None:
        self._estoque = estoque

    def notificar(self, evento: Evento) -> None:
        if evento.tipo == "PEDIDO_ENTREGUE":
            itens = evento.dados.get("itens", [])
            pedido_id = evento.dados.get("pedido_id", "?")

            for item in itens:
                produto_id = item["produto_id"]
                quantidade = item["quantidade"]

                if self._estoque.tem_saldo_suficiente(produto_id, quantidade):
                    self._estoque.saida(
                        produto_id,
                        quantidade,
                        motivo=f"Entrega do pedido {pedido_id}",
                    )