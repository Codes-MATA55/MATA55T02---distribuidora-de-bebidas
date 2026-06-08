"""
=============================================================
TESTES UNITÁRIOS — Domínio OO
=============================================================
Cobrem: Value Objects, Entidades, Hierarquia de Usuários,
        Permissões, Pedido e Cupom.
=============================================================
"""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "distribuidora.settings")

from apps.dominio import (
    Volume, PrecoUnitario, CodigoCupom,
    CategoriaBebida, Bebida, Lote, Estoque, Cupom,
    ItemPedido, Pedido,
    Administrador, Gerente, Vendedor, Estoquista,
    TipoDesconto, TipoVenda, StatusPedido, criar_usuario,
)
from datetime import date, timedelta


# ─── Value Objects ───────────────────────────────────────────

class TestVolume:
    def test_cria_valido(self):
        v = Volume(350)
        assert v.ml == 350

    def test_rejeita_negativo(self):
        with pytest.raises(ValueError):
            Volume(-1)

    def test_str_ml(self):
        assert str(Volume(350)) == "350ml"

    def test_str_litros(self):
        assert str(Volume(2000)) == "2.0L"


class TestPrecoUnitario:
    def test_cria_valido(self):
        p = PrecoUnitario(9.90)
        assert p.valor == 9.90

    def test_rejeita_negativo(self):
        with pytest.raises(ValueError):
            PrecoUnitario(-5)

    def test_desconto_percentual(self):
        p = PrecoUnitario(100.0)
        p2 = p.aplicar_desconto_percentual(10)
        assert p2.valor == 90.0

    def test_desconto_invalido(self):
        with pytest.raises(ValueError):
            PrecoUnitario(100).aplicar_desconto_percentual(150)


class TestCodigoCupom:
    def test_normaliza_maiusculo(self):
        c = CodigoCupom("promo10")
        assert c.codigo == "PROMO10"

    def test_rejeita_curto(self):
        with pytest.raises(ValueError):
            CodigoCupom("AB")


# ─── Entidades ───────────────────────────────────────────────

class TestCategoriaBebida:
    def test_cria_valida(self):
        c = CategoriaBebida("Cerveja", "Fermentada", True)
        assert c.nome == "Cerveja"
        assert c.alcoolica is True

    def test_atualiza(self):
        c = CategoriaBebida("Suco", "Natural", False)
        c.atualizar(nome="Suco Premium")
        assert c.nome == "Suco Premium"

    def test_nome_invalido(self):
        with pytest.raises(ValueError):
            CategoriaBebida("A", "", False)


class TestBebida:
    def _bebida(self):
        return Bebida("Skol Lata", "cat-001", "Skol", 350, 3.50, "AmBev", 4.7)

    def test_cria(self):
        b = self._bebida()
        assert b.nome == "Skol Lata"
        assert b.preco.valor == 3.50

    def test_desativar(self):
        b = self._bebida()
        b.desativar()
        assert b.ativo is False

    def test_editar_preco(self):
        b = self._bebida()
        b.atualizar(preco_unitario=4.00)
        assert b.preco.valor == 4.00


class TestLoteEstoque:
    def _lote(self, qtd=100):
        return Lote(
            bebida_id="beb-001",
            quantidade=qtd,
            data_fabricacao=date.today() - timedelta(days=30),
            data_validade=date.today() + timedelta(days=365),
            codigo_lote="TST-001",
        )

    def test_baixar_ok(self):
        lote = self._lote(100)
        lote.baixar(40)
        assert lote.quantidade_disponivel == 60

    def test_baixar_insuficiente(self):
        lote = self._lote(10)
        with pytest.raises(ValueError):
            lote.baixar(20)

    def test_estoque_fefo(self):
        estoque = Estoque("beb-001")
        lote1 = Lote("beb-001", 50, date.today() - timedelta(10), date.today() + timedelta(30), "L1")
        lote2 = Lote("beb-001", 50, date.today() - timedelta(5),  date.today() + timedelta(60), "L2")
        estoque.adicionar_lote(lote1)
        estoque.adicionar_lote(lote2)
        estoque.baixar(60)
        # L1 vence antes — deve ser zerado primeiro
        assert lote1.quantidade_disponivel == 0
        assert lote2.quantidade_disponivel == 40


# ─── Hierarquia de Usuários ──────────────────────────────────

class TestUsuarios:
    def test_administrador_tem_todas_permissoes(self):
        admin = Administrador(nome="Admin", login="admin", senha_uid="uid-001")
        assert admin.tem_permissao("bebida:criar")
        assert admin.tem_permissao("usuario:remover")

    def test_vendedor_nao_cria_bebida(self):
        v = Vendedor(nome="Maria", login="maria", senha_uid="uid-002")
        assert not v.tem_permissao("bebida:criar")

    def test_vendedor_realiza_venda(self):
        v = Vendedor(nome="Maria", login="maria", senha_uid="uid-002")
        assert v.tem_permissao("venda:realizar")

    def test_estoquista_nao_vende(self):
        e = Estoquista(nome="João", login="joao", senha_uid="uid-003")
        assert not e.tem_permissao("venda:realizar")

    def test_gerente_nao_remove_usuario(self):
        g = Gerente(nome="Carlos", login="carlos", senha_uid="uid-004")
        assert not g.tem_permissao("usuario:remover")

    def test_verificar_senha_correta(self):
        admin = Administrador(nome="Admin", login="admin", senha_uid="minha-senha")
        assert admin.verificar_senha("minha-senha")

    def test_verificar_senha_errada(self):
        admin = Administrador(nome="Admin", login="admin", senha_uid="minha-senha")
        assert not admin.verificar_senha("errada")

    def test_factory_cria_tipo_correto(self):
        u = criar_usuario("vendas", nome="X", login="x", senha_uid="y")
        assert isinstance(u, Vendedor)


# ─── Cupom ───────────────────────────────────────────────────

class TestCupom:
    def _cupom_percentual(self):
        return Cupom(
            codigo="PROMO10",
            descricao="10%",
            tipo_desconto=TipoDesconto.PERCENTUAL,
            valor_desconto=10.0,
            valor_minimo_pedido=50.0,
            usos_maximos=100,
            valido_de=date.today() - timedelta(1),
            valido_ate=date.today() + timedelta(30),
        )

    def test_desconto_percentual(self):
        c = self._cupom_percentual()
        assert c.calcular_desconto(100.0) == 10.0

    def test_desconto_fixo(self):
        c = Cupom(
            codigo="DESC20",
            descricao="R$20",
            tipo_desconto=TipoDesconto.FIXO,
            valor_desconto=20.0,
            valor_minimo_pedido=100.0,
            usos_maximos=10,
            valido_de=date.today() - timedelta(1),
            valido_ate=date.today() + timedelta(30),
        )
        assert c.calcular_desconto(150.0) == 20.0

    def test_cupom_expirado(self):
        c = Cupom(
            codigo="VELHO",
            descricao="Expirado",
            tipo_desconto=TipoDesconto.PERCENTUAL,
            valor_desconto=5.0,
            valor_minimo_pedido=0,
            usos_maximos=10,
            valido_de=date(2020, 1, 1),
            valido_ate=date(2020, 12, 31),
        )
        with pytest.raises(ValueError):
            c.calcular_desconto(100)

    def test_valor_minimo_nao_atingido(self):
        c = self._cupom_percentual()
        with pytest.raises(ValueError):
            c.calcular_desconto(30.0)


# ─── Pedido ──────────────────────────────────────────────────

class TestPedido:
    def _pedido(self):
        return Pedido(usuario_id="usr-001", tipo_venda=TipoVenda.INDIVIDUAL)

    def _item(self, qtd=2, preco=10.0):
        return ItemPedido("beb-001", "Skol Lata", qtd, preco)

    def test_valor_bruto(self):
        p = self._pedido()
        p.adicionar_item(self._item(3, 5.0))
        assert p.valor_bruto == 15.0

    def test_confirmar(self):
        p = self._pedido()
        p.adicionar_item(self._item())
        p.confirmar()
        assert p.status == StatusPedido.CONFIRMADO

    def test_confirmar_sem_itens(self):
        with pytest.raises(ValueError):
            self._pedido().confirmar()

    def test_cancelar(self):
        p = self._pedido()
        p.adicionar_item(self._item())
        p.cancelar()
        assert p.status == StatusPedido.CANCELADO

    def test_aplicar_cupom(self):
        p = self._pedido()
        p.adicionar_item(self._item(10, 10.0))  # bruto=100
        cupom = Cupom(
            codigo="TEST10",
            descricao="10%",
            tipo_desconto=TipoDesconto.PERCENTUAL,
            valor_desconto=10.0,
            valor_minimo_pedido=0,
            usos_maximos=99,
            valido_de=date.today() - timedelta(1),
            valido_ate=date.today() + timedelta(30),
        )
        p.aplicar_cupom(cupom)
        assert p.desconto_aplicado == 10.0
        assert p.valor_final == 90.0
