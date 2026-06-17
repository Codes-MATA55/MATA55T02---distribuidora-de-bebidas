import unittest
from domain.entities.produto import Produto


class TestProduto(unittest.TestCase):
    def setUp(self):
        self.produto_valido = Produto(
            marca="Ambev",
            nome="Cerveja Antarctica",
            descricao="Lata 350ml",
            codigo_barras="7891000100011",
            preco=4.50,
            quantidade_estoque=100,
            fornecedor="Distribuidora Central"
        )

    def test_criar_produto_sucesso(self):
        self.assertEqual(self.produto_valido.nome, "Cerveja Antarctica")
        self.assertEqual(self.produto_valido.quantidade_estoque, 100)

    def test_preco_negativo(self):
        with self.assertRaises(ValueError):
            Produto("Ambev", "Nome", "Desc", "123", -1.0, 10, "Fornecedor")

    def test_estoque_inicial_negativo(self):
        with self.assertRaises(ValueError):
            Produto("Ambev", "Nome", "Desc", "123", 4.50, -5, "Fornecedor")

    def test_adicionar_estoque(self):
        self.produto_valido.adicionar_estoque(50)
        self.assertEqual(self.produto_valido.quantidade_estoque, 150)

    def test_erro_quantidade_invalida(self):
        with self.assertRaises(ValueError):
            self.produto_valido.adicionar_estoque(0)

    def test_remover_estoque(self):
        self.produto_valido.remover_estoque(40)
        self.assertEqual(self.produto_valido.quantidade_estoque, 60)

    def test_erro_remover_saldo(self):
        with self.assertRaises(ValueError):
            self.produto_valido.remover_estoque(150)
