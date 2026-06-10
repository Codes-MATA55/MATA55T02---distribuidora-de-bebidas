from datetime import date
from domain.entities.produto import Produto
from domain.value_objects.ids import LoteId


class Lote:
    def __init__(self, produto: Produto, quantidade_inicial: int, data_validade: date, id: LoteId = None):
        if quantidade_inicial <= 0:
            raise ValueError("A quantidade inicial do lote deve ser maior que zero")
        if not isinstance(data_validade, date):
            raise ValueError("A data de validade deve ser um objeto válido do tipo date")
        
        self._id = id or LoteId()
        self._produto = produto
        self._quantidade_inicial = quantidade_inicial
        self._quantidade_atual = quantidade_inicial
        self._data_validade = data_validade

    @property
    def id(self) -> int:
        return self._id

    @property
    def produto(self) -> Produto:
        return self._produto

    @property
    def quantidade_inicial(self) -> int:
        return self._quantidade_inicial

    @property
    def quantidade_atual(self) -> int:
        return self._quantidade_atual

    @property
    def data_validade(self) -> date:
        return self._data_validade

    def esta_vencido(self, data_referencia: date = None) -> bool:
        # Verifica se o lote está vencido com base em uma data de referência (padrão: hoje).
        if data_referencia is None:
            data_referencia = date.today()
        return self._data_validade < data_referencia

    def consumir_quantidade(self, quantidade: int):
        # Consome uma quantidade do lote garantindo que não fique negativa.
        if quantidade <= 0:
            raise ValueError("A quantidade a ser consumida deve ser maior que zero")
        if quantidade > self._quantidade_atual:
            raise ValueError(
                f"Saldo insuficiente no lote {self._id}. "
                f"Disponível: {self._quantidade_atual}, Solicitado: {quantidade}"
            )
        self._quantidade_atual -= quantidade
