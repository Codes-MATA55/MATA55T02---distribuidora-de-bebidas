from datetime import datetime
from enum import Enum


class Produto:

	def __init__(self, marca, nome, descricao, codbarras, preco, qtestoque, fornecedor):
		self.marca = marca
		self.nome = nome
		self.descricao = descricao
		self.codbarras = codbarras
		self.preco = preco
		self.qtestoque = qtestoque
		self.fornecedor = fornecedor

	def adicionar_estoque(self, quantidade):
		self.qtestoque += quantidade

	def remover_estoque(self, quantidade):
		if quantidade > self.qtestoque:
			print("acabou né pai…")
		self.qtestoque -= quantidade


class Tipo_movimentacao(Enum):
	ENTRADA = "ENTRADA"
	SAIDA = "SAÍDA"

class Movimentacao_estoque:
	def __init__(self, id, produto, tipo, quantidade):
		self.id = id
		self.produto = produto
		self.tipo = tipo
		self.quantidade = quantidade
		self.data = datetime.now()

		self.atualizar_estoque()

	def atualizar_estoque(self):
		if self.tipo == Tipo_movimentacao.ENTRADA:
			self.produto.adicionar_estoque(self.quantidade)
		elif self.tipo == Tipo_movimentacao.SAIDA:
			self.produto.remover_estoque(self.quantidade)

class Usuario:
	def __init__(self, id, nome, cargo):
		self.id = id
		self.nome = nome
		self.cargo = cargo

class Cargo:
	def __init__(self, id, nome, funcao, salario):
		self.id = id
		self.nome = nome
		self.funcao = funcao
		self.salario = salario

class Marca:
	def __init__(self, id, nome):
		self.id = id
		self.nome = nome

class Categoria:
	def __init__(self, id, nome):
		self.id = id
		self.nome = nome

class Fornecedor:
		
	def __init__(self, id, nome, endereco, telefone, cnpj):
		self.id = id
		self.nome = nome
		self.endereco = endereco
		self.telefone = telefone
		self.cnpj = cnpj