"""
Testes Unitários: Controle de Estoque
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import unittest
from src.bebida.cerveja import Cerveja
from src.bebida.refrigerante import Refrigerante
from src.estoque.estoque import Estoque
from src.estoque.movimentacao import TipoMovimentacao
from src.exceptions.regras_negocio import EstoqueInsuficienteException


def _cerveja() -> Cerveja:
    return Cerveja(nome="Pilsen Test", volume_ml=350, preco_unitario=4.50)


def _refrigerante() -> Refrigerante:
    return Refrigerante(nome="Cola Test", volume_ml=600, preco_unitario=3.20)


class TestEstoqueEntradaSaida(unittest.TestCase):

    def setUp(self):
        self.estoque = Estoque()
        self.cerveja = _cerveja()
        self.estoque.registrar_produto(self.cerveja)

    def test_saldo_inicial_zero(self):
        self.assertEqual(self.estoque.consultar_saldo(self.cerveja.id), 0)

    def test_entrada_aumenta_saldo(self):
        self.estoque.entrada(self.cerveja.id, 100, "Teste")
        self.assertEqual(self.estoque.consultar_saldo(self.cerveja.id), 100)

    def test_saida_diminui_saldo(self):
        self.estoque.entrada(self.cerveja.id, 100, "Teste")
        self.estoque.saida(self.cerveja.id, 30, "Pedido")
        self.assertEqual(self.estoque.consultar_saldo(self.cerveja.id), 70)

    def test_multiplas_entradas_acumulam(self):
        self.estoque.entrada(self.cerveja.id, 100, "Lote 1")
        self.estoque.entrada(self.cerveja.id, 200, "Lote 2")
        self.assertEqual(self.estoque.consultar_saldo(self.cerveja.id), 300)

    def test_saida_exata_zera_estoque(self):
        self.estoque.entrada(self.cerveja.id, 50, "Teste")
        self.estoque.saida(self.cerveja.id, 50, "Total")
        self.assertEqual(self.estoque.consultar_saldo(self.cerveja.id), 0)

    def test_saida_com_estoque_insuficiente_lanca_excecao(self):
        self.estoque.entrada(self.cerveja.id, 10, "Pouco")
        with self.assertRaises(EstoqueInsuficienteException):
            self.estoque.saida(self.cerveja.id, 11, "Demais")

    def test_saida_sem_saldo_lanca_excecao(self):
        with self.assertRaises(EstoqueInsuficienteException):
            self.estoque.saida(self.cerveja.id, 1, "Vazio")

    def test_entrada_negativa_lanca_excecao(self):
        with self.assertRaises(ValueError):
            self.estoque.entrada(self.cerveja.id, -10, "Inválido")

    def test_saida_negativa_lanca_excecao(self):
        with self.assertRaises(ValueError):
            self.estoque.saida(self.cerveja.id, -5, "Inválido")

    def test_produto_nao_registrado_lanca_excecao(self):
        with self.assertRaises(KeyError):
            self.estoque.entrada("id-inexistente", 10, "Teste")


class TestEstoqueHistorico(unittest.TestCase):

    def setUp(self):
        self.estoque = Estoque()
        self.cerveja = _cerveja()
        self.estoque.registrar_produto(self.cerveja)

    def test_historico_vazio_inicialmente(self):
        self.assertEqual(len(self.estoque.historico_completo()), 0)

    def test_entrada_gera_movimentacao(self):
        self.estoque.entrada(self.cerveja.id, 100, "Teste")
        hist = self.estoque.historico_completo()
        self.assertEqual(len(hist), 1)
        self.assertEqual(hist[0].tipo, TipoMovimentacao.ENTRADA)
        self.assertEqual(hist[0].quantidade, 100)

    def test_saida_gera_movimentacao(self):
        self.estoque.entrada(self.cerveja.id, 100, "Entrada")
        self.estoque.saida(self.cerveja.id, 30, "Saída")
        hist = self.estoque.historico_completo()
        self.assertEqual(len(hist), 2)
        self.assertEqual(hist[1].tipo, TipoMovimentacao.SAIDA)

    def test_historico_por_produto(self):
        ref = _refrigerante()
        self.estoque.registrar_produto(ref)
        self.estoque.entrada(self.cerveja.id, 100, "Cerveja entrada")
        self.estoque.entrada(ref.id, 50, "Refri entrada")
        hist_cerveja = self.estoque.historico_produto(self.cerveja.id)
        hist_refri = self.estoque.historico_produto(ref.id)
        self.assertEqual(len(hist_cerveja), 1)
        self.assertEqual(len(hist_refri), 1)

    def test_movimentacao_imutavel(self):
        self.estoque.entrada(self.cerveja.id, 10, "Teste")
        mov = self.estoque.historico_completo()[0]
        with self.assertRaises((AttributeError, TypeError)):
            mov.quantidade = 999


class TestEstoqueTem_Saldo(unittest.TestCase):

    def setUp(self):
        self.estoque = Estoque()
        self.cerveja = _cerveja()
        self.estoque.registrar_produto(self.cerveja)

    def test_tem_saldo_suficiente_true(self):
        self.estoque.entrada(self.cerveja.id, 100, "Teste")
        self.assertTrue(self.estoque.tem_saldo_suficiente(self.cerveja.id, 100))

    def test_tem_saldo_suficiente_false(self):
        self.estoque.entrada(self.cerveja.id, 5, "Teste")
        self.assertFalse(self.estoque.tem_saldo_suficiente(self.cerveja.id, 10))

    def test_produto_nao_registrado_retorna_false(self):
        self.assertFalse(self.estoque.tem_saldo_suficiente("nao-existe", 1))


if __name__ == "__main__":
    unittest.main(verbosity=2)
