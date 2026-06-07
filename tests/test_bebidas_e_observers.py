"""Testes Unitarios: Bebidas e Observadores"""
import unittest
from src.bebida.cerveja import Cerveja
from src.bebida.refrigerante import Refrigerante
from src.bebida.suco import Suco
from src.observadores.observer import EventBus, Evento
from src.observadores.logger import LoggerObserver, MonitoramentoObserver
from src.pedido.pedido import Pedido
from src.pedido.item_pedido import ItemPedido


class TestCerveja(unittest.TestCase):

    def test_criacao_valida(self):
        c = Cerveja(
            nome="Pilsen", volume_ml=350,
            preco_unitario=4.50, teor_alcoolico=4.8,
        )
        self.assertEqual(c.categoria, "Cerveja")

    def test_teor_alcoolico_invalido_acima(self):
        with self.assertRaises(ValueError):
            Cerveja(
                nome="Pilsen", volume_ml=350,
                preco_unitario=4.50, teor_alcoolico=25.0,
            )

    def test_teor_alcoolico_negativo(self):
        with self.assertRaises(ValueError):
            Cerveja(
                nome="Pilsen", volume_ml=350,
                preco_unitario=4.50, teor_alcoolico=-1.0,
            )

    def test_volume_negativo(self):
        with self.assertRaises(ValueError):
            Cerveja(nome="Pilsen", volume_ml=-1, preco_unitario=4.50)

    def test_preco_negativo(self):
        with self.assertRaises(ValueError):
            Cerveja(nome="Pilsen", volume_ml=350, preco_unitario=-1.0)

    def test_descricao_completa(self):
        c = Cerveja(nome="Pilsen", volume_ml=350, preco_unitario=4.50)
        desc = c.descricao_completa()
        self.assertIn("Cerveja", desc)
        self.assertIn("Pilsen", desc)


class TestRefrigerante(unittest.TestCase):

    def test_criacao_valida(self):
        r = Refrigerante(
            nome="Cola", volume_ml=600,
            preco_unitario=3.20, sabor="Cola",
        )
        self.assertEqual(r.categoria, "Refrigerante")

    def test_variante_diet(self):
        r = Refrigerante(
            nome="Cola Zero", volume_ml=600,
            preco_unitario=3.20, is_diet=True,
        )
        self.assertIn("Zero", r.descricao_completa())


class TestSuco(unittest.TestCase):

    def test_criacao_valida(self):
        s = Suco(
            nome="Laranja", volume_ml=1000,
            preco_unitario=8.90, percentual_polpa=100.0,
        )
        self.assertEqual(s.categoria, "Suco")

    def test_polpa_acima_de_100(self):
        with self.assertRaises(ValueError):
            Suco(
                nome="Laranja", volume_ml=1000,
                preco_unitario=8.90, percentual_polpa=101.0,
            )

    def test_polpa_negativa(self):
        with self.assertRaises(ValueError):
            Suco(
                nome="Laranja", volume_ml=1000,
                preco_unitario=8.90, percentual_polpa=-5.0,
            )


class TestItemPedido(unittest.TestCase):

    def test_valor_total_calculado(self):
        c = Cerveja(nome="Pilsen", volume_ml=350, preco_unitario=10.0)
        item = ItemPedido(c.id, c, 5)
        self.assertAlmostEqual(item.valor_total, 50.0)

    def test_quantidade_zero_invalida(self):
        c = Cerveja(nome="Pilsen", volume_ml=350, preco_unitario=10.0)
        with self.assertRaises(ValueError):
            ItemPedido(c.id, c, 0)

    def test_quantidade_negativa_invalida(self):
        c = Cerveja(nome="Pilsen", volume_ml=350, preco_unitario=10.0)
        with self.assertRaises(ValueError):
            ItemPedido(c.id, c, -3)


class TestObserverPattern(unittest.TestCase):

    def setUp(self):
        self.event_bus = EventBus()
        self.logger = LoggerObserver()
        self.monitoramento = MonitoramentoObserver()

    def test_logger_recebe_evento(self):
        self.event_bus.assinar("PEDIDO_SEPARADO", self.logger)
        evento = Evento(
            tipo="PEDIDO_SEPARADO", dados={"pedido_id": "123"}
        )
        self.event_bus.publicar(evento)
        self.assertEqual(len(self.logger.obter_logs()), 1)

    def test_monitoramento_conta_eventos(self):
        self.event_bus.assinar("PEDIDO_ENTREGUE", self.monitoramento)
        for _ in range(5):
            self.event_bus.publicar(
                Evento(tipo="PEDIDO_ENTREGUE", dados={})
            )
        self.assertEqual(
            self.monitoramento.metricas()["PEDIDO_ENTREGUE"], 5
        )

    def test_evento_sem_assinantes_nao_lanca_erro(self):
        self.event_bus.publicar(
            Evento(tipo="EVENTO_SEM_ASSINANTES", dados={})
        )

    def test_multiplos_assinantes_recebem_mesmo_evento(self):
        logger2 = LoggerObserver()
        self.event_bus.assinar("PEDIDO_SEPARADO", self.logger)
        self.event_bus.assinar("PEDIDO_SEPARADO", logger2)
        self.event_bus.publicar(
            Evento(tipo="PEDIDO_SEPARADO", dados={})
        )
        self.assertEqual(len(self.logger.obter_logs()), 1)
        self.assertEqual(len(logger2.obter_logs()), 1)

    def test_pedido_publica_evento_ao_separar(self):
        self.event_bus.assinar("PEDIDO_SEPARADO", self.monitoramento)
        c = Cerveja(nome="Pilsen", volume_ml=350, preco_unitario=4.50)
        p = Pedido(cliente="Cliente", event_bus=self.event_bus)
        p.adicionar_item(ItemPedido(c.id, c, 10))
        p.iniciar_separacao()
        p.finalizar_separacao()
        self.assertEqual(
            self.monitoramento.metricas().get("PEDIDO_SEPARADO", 0), 1
        )

    def test_pedido_publica_evento_ao_entregar(self):
        self.event_bus.assinar("PEDIDO_ENTREGUE", self.monitoramento)
        c = Cerveja(nome="Pilsen", volume_ml=350, preco_unitario=4.50)
        p = Pedido(cliente="Cliente", event_bus=self.event_bus)
        p.adicionar_item(ItemPedido(c.id, c, 10))
        p.iniciar_separacao()
        p.finalizar_separacao()
        p.iniciar_expedicao()
        p.confirmar_entrega()
        self.assertEqual(
            self.monitoramento.metricas().get("PEDIDO_ENTREGUE", 0), 1
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
