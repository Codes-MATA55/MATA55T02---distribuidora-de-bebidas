"""Testes Unitarios: Separacao e Expedicao"""
import unittest
from src.bebida.cerveja import Cerveja
from src.bebida.suco import Suco
from src.estoque.estoque import Estoque
from src.pedido.pedido import Pedido
from src.pedido.item_pedido import ItemPedido
from src.separacao.fifo import FIFOSeparacao
from src.expedicao.regras import ValidadorExpedicao
from src.exceptions.regras_negocio import (
    EstoqueInsuficienteException,
    RegraDeExpedicaoVioladaException,
)


def _setup():
    estoque = Estoque()
    cerveja = Cerveja(nome="Pilsen", volume_ml=350, preco_unitario=4.50)
    suco = Suco(nome="Laranja", volume_ml=1000, preco_unitario=8.90)
    estoque.registrar_produto(cerveja)
    estoque.registrar_produto(suco)
    estoque.entrada(cerveja.id, 1000, "Lote inicial")
    estoque.entrada(suco.id, 500, "Lote inicial")
    return estoque, cerveja, suco


class TestFIFOSeparacao(unittest.TestCase):

    def setUp(self):
        self.estoque, self.cerveja, self.suco = _setup()
        self.estrategia = FIFOSeparacao()

    def test_nome_estrategia(self):
        self.assertEqual(self.estrategia.nome, "FIFO")

    def test_separacao_bem_sucedida(self):
        pedido = Pedido(cliente="Cliente A")
        pedido.adicionar_item(
            ItemPedido(self.cerveja.id, self.cerveja, 100)
        )
        self.estrategia.separar(pedido, self.estoque)
        self.assertEqual(pedido.estado_atual, "Separado")

    def test_separacao_deduz_estoque(self):
        pedido = Pedido(cliente="Cliente B")
        pedido.adicionar_item(
            ItemPedido(self.cerveja.id, self.cerveja, 200)
        )
        saldo_antes = self.estoque.consultar_saldo(self.cerveja.id)
        self.estrategia.separar(pedido, self.estoque)
        saldo_depois = self.estoque.consultar_saldo(self.cerveja.id)
        self.assertEqual(saldo_antes - saldo_depois, 200)

    def test_separacao_com_multiplos_itens(self):
        pedido = Pedido(cliente="Cliente C")
        pedido.adicionar_item(
            ItemPedido(self.cerveja.id, self.cerveja, 50)
        )
        pedido.adicionar_item(
            ItemPedido(self.suco.id, self.suco, 30)
        )
        self.estrategia.separar(pedido, self.estoque)
        self.assertEqual(pedido.estado_atual, "Separado")
        self.assertEqual(
            self.estoque.consultar_saldo(self.cerveja.id), 950
        )
        self.assertEqual(
            self.estoque.consultar_saldo(self.suco.id), 470
        )

    def test_separacao_sem_estoque_lanca_excecao(self):
        pedido = Pedido(cliente="Cliente D")
        pedido.adicionar_item(
            ItemPedido(self.cerveja.id, self.cerveja, 9999)
        )
        with self.assertRaises(EstoqueInsuficienteException):
            self.estrategia.separar(pedido, self.estoque)

    def test_pedido_permanece_criado_se_separacao_falha(self):
        pedido = Pedido(cliente="Cliente E")
        pedido.adicionar_item(
            ItemPedido(self.cerveja.id, self.cerveja, 9999)
        )
        try:
            self.estrategia.separar(pedido, self.estoque)
        except EstoqueInsuficienteException:
            pass
        self.assertEqual(pedido.estado_atual, "Criado")

    def test_historico_de_movimentacao_apos_separacao(self):
        pedido = Pedido(cliente="Cliente F")
        pedido.adicionar_item(
            ItemPedido(self.cerveja.id, self.cerveja, 10)
        )
        self.estrategia.separar(pedido, self.estoque)
        hist = self.estoque.historico_produto(self.cerveja.id)
        self.assertEqual(len(hist), 2)


class TestValidadorExpedicao(unittest.TestCase):

    def setUp(self):
        self.estoque, self.cerveja, self.suco = _setup()
        self.validador = ValidadorExpedicao()
        self.estrategia = FIFOSeparacao()

    def _pedido_separado(self) -> Pedido:
        pedido = Pedido(cliente="Cliente X")
        pedido.adicionar_item(
            ItemPedido(self.cerveja.id, self.cerveja, 10)
        )
        self.estrategia.separar(pedido, self.estoque)
        return pedido

    def test_pedido_separado_passa_validacao(self):
        pedido = self._pedido_separado()
        self.validador.validar(pedido, self.estoque)

    def test_pedido_criado_falha_validacao(self):
        pedido = Pedido(cliente="Sem Separar")
        pedido.adicionar_item(
            ItemPedido(self.cerveja.id, self.cerveja, 10)
        )
        with self.assertRaises(RegraDeExpedicaoVioladaException):
            self.validador.validar(pedido, self.estoque)

    def test_pedido_sem_itens_falha_validacao(self):
        pedido = Pedido(cliente="Vazio")
        with self.assertRaises(RegraDeExpedicaoVioladaException):
            self.validador.validar(pedido, self.estoque)

    def test_excecao_contem_lista_de_violacoes(self):
        pedido = Pedido(cliente="Sem itens")
        try:
            self.validador.validar(pedido, self.estoque)
        except RegraDeExpedicaoVioladaException as e:
            self.assertIsInstance(e.violacoes, list)
            self.assertGreater(len(e.violacoes), 0)

    def test_fluxo_expedicao_completo_apos_validacao(self):
        pedido = self._pedido_separado()
        self.validador.validar(pedido, self.estoque)
        pedido.iniciar_expedicao()
        self.assertEqual(pedido.estado_atual, "EmExpedicao")
        pedido.confirmar_entrega()
        self.assertEqual(pedido.estado_atual, "Entregue")


if __name__ == "__main__":
    unittest.main(verbosity=2)