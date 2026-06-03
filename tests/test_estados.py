"""
Testes Unitários: Mudança de Estados do Pedido
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import unittest
from src.bebida.cerveja import Cerveja
from src.pedido.pedido import Pedido
from src.pedido.item_pedido import ItemPedido
from src.exceptions.regras_negocio import TransicaoDeEstadoInvalidaException


def _cerveja() -> Cerveja:
    return Cerveja(nome="Pilsen Test", volume_ml=350, preco_unitario=4.50)


def _pedido_com_item() -> Pedido:
    p = Pedido(cliente="Cliente Teste")
    c = _cerveja()
    p.adicionar_item(ItemPedido(c.id, c, 10))
    return p


class TestEstadosCriado(unittest.TestCase):

    def test_estado_inicial_e_criado(self):
        p = _pedido_com_item()
        self.assertEqual(p.estado_atual, "Criado")

    def test_criado_para_em_separacao(self):
        p = _pedido_com_item()
        p.iniciar_separacao()
        self.assertEqual(p.estado_atual, "Em separaçao")

    def test_criado_para_cancelado(self):
        p = _pedido_com_item()
        p.cancelar()
        self.assertEqual(p.estado_atual, "Cancelado")

    def test_criado_nao_pode_ir_para_entregue(self):
        p = _pedido_com_item()
        with self.assertRaises(TransicaoDeEstadoInvalidaException):
            p.confirmar_entrega()

    def test_criado_nao_pode_iniciar_expedicao(self):
        p = _pedido_com_item()
        with self.assertRaises(TransicaoDeEstadoInvalidaException):
            p.iniciar_expedicao()

    def test_sem_itens_nao_inicia_separacao(self):
        p = Pedido(cliente="Sem Itens")
        with self.assertRaises(ValueError):
            p.iniciar_separacao()

    def test_nao_adiciona_item_apos_iniciar_separacao(self):
        p = _pedido_com_item()
        p.iniciar_separacao()
        c = _cerveja()
        with self.assertRaises(ValueError):
            p.adicionar_item(ItemPedido(c.id, c, 5))


class TestEstadosEmSeparacao(unittest.TestCase):

    def _pedido_em_separacao(self) -> Pedido:
        p = _pedido_com_item()
        p.iniciar_separacao()
        return p

    def test_em_separacao_para_separado(self):
        p = self._pedido_em_separacao()
        p.finalizar_separacao()
        self.assertEqual(p.estado_atual, "Separado")

    def test_em_separacao_para_cancelado(self):
        p = self._pedido_em_separacao()
        p.cancelar()
        self.assertEqual(p.estado_atual, "Cancelado")

    def test_em_separacao_nao_pode_confirmar_entrega(self):
        p = self._pedido_em_separacao()
        with self.assertRaises(TransicaoDeEstadoInvalidaException):
            p.confirmar_entrega()


class TestEstadosSeparado(unittest.TestCase):

    def _pedido_separado(self) -> Pedido:
        p = _pedido_com_item()
        p.iniciar_separacao()
        p.finalizar_separacao()
        return p

    def test_separado_para_em_expedicao(self):
        p = self._pedido_separado()
        p.iniciar_expedicao()
        self.assertEqual(p.estado_atual, "Em expedição")

    def test_separado_nao_pode_cancelar(self):
        p = self._pedido_separado()
        with self.assertRaises(TransicaoDeEstadoInvalidaException):
            p.cancelar()

    def test_separado_nao_pode_confirmar_entrega(self):
        p = self._pedido_separado()
        with self.assertRaises(TransicaoDeEstadoInvalidaException):
            p.confirmar_entrega()


class TestEstadosEmExpedicao(unittest.TestCase):

    def _pedido_em_expedicao(self) -> Pedido:
        p = _pedido_com_item()
        p.iniciar_separacao()
        p.finalizar_separacao()
        p.iniciar_expedicao()
        return p

    def test_em_expedicao_para_entregue(self):
        p = self._pedido_em_expedicao()
        p.confirmar_entrega()
        self.assertEqual(p.estado_atual, "Entregue")

    def test_em_expedicao_nao_pode_cancelar(self):
        p = self._pedido_em_expedicao()
        with self.assertRaises(TransicaoDeEstadoInvalidaException):
            p.cancelar()


class TestEstadosTerminais(unittest.TestCase):

    def test_entregue_nao_aceita_nenhuma_transicao(self):
        p = _pedido_com_item()
        p.iniciar_separacao()
        p.finalizar_separacao()
        p.iniciar_expedicao()
        p.confirmar_entrega()
        for operacao in [p.cancelar, p.iniciar_separacao, p.iniciar_expedicao, p.confirmar_entrega]:
            with self.assertRaises(TransicaoDeEstadoInvalidaException):
                operacao()

    def test_cancelado_nao_aceita_nenhuma_transicao(self):
        p = _pedido_com_item()
        p.cancelar()
        for operacao in [p.cancelar, p.iniciar_separacao, p.iniciar_expedicao, p.confirmar_entrega]:
            with self.assertRaises(TransicaoDeEstadoInvalidaException):
                operacao()

    def test_historico_completo_de_estados(self):
        p = _pedido_com_item()
        p.iniciar_separacao()
        p.finalizar_separacao()
        p.iniciar_expedicao()
        p.confirmar_entrega()
        self.assertEqual(
            p.historico_estados,
            ["Criado", "EmSeparacao", "Separado", "EmExpedicao", "Entregue"]
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
