import unittest
from src.domain.produtos.produto import Produto
from src.domain.estoque.tipo_movimentacao import TipoMovimentacao
from src.domain.estoque.movimentacao_estoque import MovimentacaoEstoque

class TestEstoque(unittest.TestCase):
    def setUp(self):
        self.produto = Produto(
            marca="Coca-Cola",
            nome="Refri Coca",
            descricao="Pet 2L",
            codbarras="7892000200022",
            preco=8.00,
            qtestoque=50,
            fornecedor="Coca-Cola BR"
        )

    def test_movimentacao_entrada_sucesso(self):
        movimentacao = MovimentacaoEstoque(
            id=1,
            produto=self.produto,
            tipo=TipoMovimentacao.ENTRADA,
            quantidade=20
        )
        self.assertEqual(self.produto.qtestoque, 70)
        self.assertEqual(movimentacao.quantidade, 20)

    def test_movimentacao_saida_sucesso(self):
        movimentacao = MovimentacaoEstoque(
            id=2,
            produto=self.produto,
            tipo=TipoMovimentacao.SAIDA,
            quantidade=10
        )
        self.assertEqual(self.produto.qtestoque, 40)

    def test_movimentacao_saida_estourar_estoque(self):
        with self.assertRaises(ValueError):
            MovimentacaoEstoque(
                id=3,
                produto=self.produto,
                tipo=TipoMovimentacao.SAIDA,
                quantidade=60
            )

    def test_quantidade_movimentacao_invalida(self):
        with self.assertRaises(ValueError):
            MovimentacaoEstoque(
                id=4,
                produto=self.produto,
                tipo=TipoMovimentacao.ENTRADA,
                quantidade=0
            )