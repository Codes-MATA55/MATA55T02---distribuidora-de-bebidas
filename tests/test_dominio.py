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
    Volume, CategoriaBebida, Bebida, Lote, Estoque,
    ItemPedido, Pedido, Administrador, Gerente, Requisitante, Estoquista,
    MotivoPedido, StatusPedido, criar_usuario,
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

    def test_desativar(self):
        b = self._bebida()
        b.desativar()
        assert b.ativo is False


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

    def test_requisitante_nao_cria_bebida(self):
        # Mudou de Vendedor para Requisitante
        r = Requisitante(nome="Maria", login="maria", senha_uid="uid-002")
        assert not r.tem_permissao("bebida:criar")

    def test_requisitante_cria_pedido(self):
        # Mudou para validar o novo fluxo de criar pedidos de movimentação
        r = Requisitante(nome="Maria", login="maria", senha_uid="uid-002")
        assert r.tem_permissao("pedido:criar")

    def test_estoquista_nao_cria_pedido(self):
        # Garante que o estoquista apenas manuseia o stock, quem pede é o requisitante
        e = Estoquista(nome="João", login="joao", senha_uid="uid-003")
        assert not e.tem_permissao("pedido:criar")

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
        # Teste da Factory: agora a string mágica "requisitante" deve criar a classe Requisitante
        u = criar_usuario("requisitante", nome="X", login="x", senha_uid="y")
        assert isinstance(u, Requisitante)


# ─── Testes do Pedido de Movimentação ──────────────────────────

class TestPedido:
    def _pedido(self):
        # Cria um pedido usando o novo Enum MotivoPedido
        return Pedido(usuario_id="usr-001", motivo=MotivoPedido.ABASTECIMENTO)

    def _item(self, qtd=2):
        # Item agora não recebe mais preço unitário
        return ItemPedido("beb-001", "Skol Lata", qtd)

    def test_confirmar_pedido_valido(self):
        p = self._pedido()
        p.adicionar_item(self._item())
        p.confirmar()
        assert p.status == StatusPedido.CONCLUIDO

    def test_rejeitar_confirmar_sem_itens(self):
        p = self._pedido()
        with pytest.raises(ValueError):
            p.confirmar()

    def test_cancelar_pedido_em_rascunho(self):
        p = self._pedido()
        p.adicionar_item(self._item())
        p.cancelar()
        assert p.status == StatusPedido.CANCELADO

    def test_proibir_adicionar_item_em_pedido_concluido(self):
        p = self._pedido()
        p.adicionar_item(self._item())
        p.confirmar()
        with pytest.raises(ValueError):
            p.adicionar_item(self._item(1))