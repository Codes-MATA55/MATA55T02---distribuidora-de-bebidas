"""
=============================================================
SERVIÇOS DE APLICAÇÃO — Casos de uso do sistema
=============================================================
Orquestram o domínio sem conter regras de negócio.
Referência: Evans DDD p.106 — Application Service
=============================================================
"""

from datetime import datetime

from .dominio import (
    Bebida, CategoriaBebida, Cupom, ItemPedido, Lote,
    Pedido, TipoDesconto, TipoVenda, UsuarioBase, criar_usuario,
)
from .repositorios import (
    RepositorioBebida, RepositorioCategoria, RepositorioCupom,
    RepositorioEstoque, RepositorioPedido, RepositorioUsuario,
)


# ─────────────────────────────────────────────────────────────
# AUTENTICAÇÃO
# ─────────────────────────────────────────────────────────────

class ServicoAutenticacao:

    def __init__(self):
        self._repo = RepositorioUsuario()

    def autenticar(self, login: str, senha_uid: str) -> UsuarioBase:
        usuario = self._repo.buscar_por_login(login)
        if not usuario or not usuario.verificar_senha(senha_uid):
            raise PermissionError("Login ou senha inválidos.")
        return usuario

    def obter_usuario(self, usuario_id: str) -> UsuarioBase:
        usuario = self._repo.buscar_por_id(usuario_id)
        if not usuario:
            raise ValueError("Usuário não encontrado.")
        return usuario


# ─────────────────────────────────────────────────────────────
# USUÁRIOS
# ─────────────────────────────────────────────────────────────

class ServicoUsuario:

    def __init__(self):
        self._repo = RepositorioUsuario()

    def listar(self, solicitante: UsuarioBase) -> list[dict]:
        self._exigir("usuario:listar", solicitante)
        return [u.para_dict() for u in self._repo.listar()]

    def criar(self, solicitante: UsuarioBase, dados: dict) -> dict:
        self._exigir("usuario:criar", solicitante)
        if self._repo.buscar_por_login(dados["login"]):
            raise ValueError(f"Login '{dados['login']}' já está em uso.")
        usuario = criar_usuario(
            tipo=dados["tipo"],
            nome=dados["nome"],
            login=dados["login"],
            senha_uid=dados["senha_uid"],
        )
        self._repo.salvar_novo(usuario, dados["senha_uid"])
        return usuario.para_dict()

    def editar(self, solicitante: UsuarioBase, usuario_id: str, dados: dict) -> dict:
        self._exigir("usuario:editar", solicitante)
        usuario = self._repo.buscar_por_id(usuario_id)
        if not usuario:
            raise ValueError("Usuário não encontrado.")
        usuario.atualizar(
            nome=dados.get("nome"),
            tipo=dados.get("tipo"),
        )
        self._repo.salvar(usuario)
        if dados.get("senha_uid"):
            self._repo.atualizar_senha(usuario_id, dados["senha_uid"])
        return usuario.para_dict()

    def remover(self, solicitante: UsuarioBase, usuario_id: str) -> bool:
        self._exigir("usuario:remover", solicitante)
        return self._repo.remover(usuario_id)

    @staticmethod
    def _exigir(permissao: str, usuario: UsuarioBase):
        if not usuario.tem_permissao(permissao):
            raise PermissionError(
                f"Usuário '{usuario.login}' ({usuario.tipo.value}) "
                f"não tem permissão: {permissao}"
            )


# ─────────────────────────────────────────────────────────────
# CATEGORIAS
# ─────────────────────────────────────────────────────────────

class ServicoCategoria:

    def __init__(self):
        self._repo = RepositorioCategoria()

    def listar(self, solicitante: UsuarioBase) -> list[dict]:
        self._exigir("categoria:listar", solicitante)
        return [c.para_dict() for c in self._repo.listar()]

    def criar(self, solicitante: UsuarioBase, dados: dict) -> dict:
        self._exigir("categoria:criar", solicitante)
        categoria = CategoriaBebida(
            nome=dados["nome"],
            descricao=dados.get("descricao", ""),
            alcoolica=dados.get("alcoolica", False),
        )
        self._repo.salvar(categoria)
        return categoria.para_dict()

    def editar(self, solicitante: UsuarioBase, categoria_id: str, dados: dict) -> dict:
        self._exigir("categoria:editar", solicitante)
        categoria = self._repo.buscar_por_id(categoria_id)
        if not categoria:
            raise ValueError("Categoria não encontrada.")
        categoria.atualizar(
            nome=dados.get("nome"),
            descricao=dados.get("descricao"),
            alcoolica=dados.get("alcoolica"),
        )
        self._repo.salvar(categoria)
        return categoria.para_dict()

    def remover(self, solicitante: UsuarioBase, categoria_id: str) -> bool:
        self._exigir("categoria:remover", solicitante)
        if not self._repo.buscar_por_id(categoria_id):
            raise ValueError("Categoria não encontrada.")
        return self._repo.remover(categoria_id)

    @staticmethod
    def _exigir(permissao: str, usuario: UsuarioBase):
        if not usuario.tem_permissao(permissao):
            raise PermissionError(
                f"Usuário '{usuario.login}' não tem permissão: {permissao}"
            )


# ─────────────────────────────────────────────────────────────
# BEBIDAS
# ─────────────────────────────────────────────────────────────

class ServicoBebida:

    def __init__(self):
        self._repo_bebida = RepositorioBebida()
        self._repo_cat = RepositorioCategoria()

    def listar(self, solicitante: UsuarioBase) -> list[dict]:
        self._exigir("bebida:listar", solicitante)
        return [b.para_dict() for b in self._repo_bebida.listar()]

    def criar(self, solicitante: UsuarioBase, dados: dict) -> dict:
        self._exigir("bebida:criar", solicitante)
        if not self._repo_cat.buscar_por_id(dados["categoria_id"]):
            raise ValueError("Categoria não encontrada.")
        bebida = Bebida(
            nome=dados["nome"],
            categoria_id=dados["categoria_id"],
            marca=dados["marca"],
            volume_ml=dados["volume_ml"],
            preco_unitario=dados["preco_unitario"],
            fornecedor=dados["fornecedor"],
            teor_alcoolico=dados.get("teor_alcoolico"),
        )
        self._repo_bebida.salvar(bebida)
        return bebida.para_dict()

    def editar(self, solicitante: UsuarioBase, bebida_id: str, dados: dict) -> dict:
        self._exigir("bebida:editar", solicitante)
        bebida = self._repo_bebida.buscar_por_id(bebida_id)
        if not bebida:
            raise ValueError("Bebida não encontrada.")
        if "categoria_id" in dados and not self._repo_cat.buscar_por_id(dados["categoria_id"]):
            raise ValueError("Categoria não encontrada.")
        bebida.atualizar(
            nome=dados.get("nome"),
            marca=dados.get("marca"),
            volume_ml=dados.get("volume_ml"),
            preco_unitario=dados.get("preco_unitario"),
            teor_alcoolico=dados.get("teor_alcoolico"),
            fornecedor=dados.get("fornecedor"),
            categoria_id=dados.get("categoria_id"),
        )
        self._repo_bebida.salvar(bebida)
        return bebida.para_dict()

    def remover(self, solicitante: UsuarioBase, bebida_id: str) -> bool:
        self._exigir("bebida:remover", solicitante)
        return self._repo_bebida.remover(bebida_id)

    @staticmethod
    def _exigir(permissao: str, usuario: UsuarioBase):
        if not usuario.tem_permissao(permissao):
            raise PermissionError(
                f"Usuário '{usuario.login}' não tem permissão: {permissao}"
            )


# ─────────────────────────────────────────────────────────────
# ESTOQUE
# ─────────────────────────────────────────────────────────────

class ServicoEstoque:

    def __init__(self):
        self._repo_estoque = RepositorioEstoque()
        self._repo_bebida = RepositorioBebida()

    def listar(self, solicitante: UsuarioBase) -> list[dict]:
        self._exigir("estoque:listar", solicitante)
        bebidas = self._repo_bebida.listar()
        resultado = []
        for b in bebidas:
            estoque = self._repo_estoque.buscar_estoque_bebida(b.id)
            dados = estoque.para_dict()
            dados["nome_bebida"] = b.nome
            resultado.append(dados)
        return resultado

    def adicionar_lote(self, solicitante: UsuarioBase, dados: dict) -> dict:
        self._exigir("estoque:adicionar", solicitante)
        from datetime import date as dt
        bebida = self._repo_bebida.buscar_por_id(dados["bebida_id"])
        if not bebida:
            raise ValueError("Bebida não encontrada.")
        lote = Lote(
            bebida_id=dados["bebida_id"],
            quantidade=dados["quantidade"],
            data_fabricacao=dt.fromisoformat(dados["data_fabricacao"]),
            data_validade=dt.fromisoformat(dados["data_validade"]),
            codigo_lote=dados["codigo_lote"],
        )
        self._repo_estoque.salvar_lote(lote)
        estoque = self._repo_estoque.buscar_estoque_bebida(dados["bebida_id"])
        self._repo_estoque.atualizar_estoque_resumo(dados["bebida_id"], estoque)
        self._repo_estoque.registrar_movimentacao(
            bebida_id=dados["bebida_id"],
            quantidade=dados["quantidade"],
            tipo="entrada",
        )
        return lote.para_dict()

    def editar_lote(self, solicitante: UsuarioBase, lote_id: str, dados: dict) -> dict:
        self._exigir("estoque:adicionar", solicitante)
        from datetime import date as dt
        lotes = self._repo_estoque.listar_lotes()
        lote = next((l for l in lotes if l.id == lote_id), None)
        if not lote:
            raise ValueError("Lote não encontrado.")
        lote.atualizar(
            data_fabricacao=dt.fromisoformat(dados["data_fabricacao"]) if "data_fabricacao" in dados else None,
            data_validade=dt.fromisoformat(dados["data_validade"]) if "data_validade" in dados else None,
            codigo_lote=dados.get("codigo_lote"),
        )
        self._repo_estoque.salvar_lote(lote)
        return lote.para_dict()

    def remover_lote(self, solicitante: UsuarioBase, lote_id: str) -> bool:
        self._exigir("estoque:remover", solicitante)
        return self._repo_estoque.remover_lote(lote_id)

    @staticmethod
    def _exigir(permissao: str, usuario: UsuarioBase):
        if not usuario.tem_permissao(permissao):
            raise PermissionError(
                f"Usuário '{usuario.login}' não tem permissão: {permissao}"
            )


# ─────────────────────────────────────────────────────────────
# CUPONS
# ─────────────────────────────────────────────────────────────

class ServicoCupom:

    def __init__(self):
        self._repo = RepositorioCupom()

    def listar(self, solicitante: UsuarioBase) -> list[dict]:
        self._exigir("cupom:listar", solicitante)
        return [c.para_dict() for c in self._repo.listar()]

    def criar(self, solicitante: UsuarioBase, dados: dict) -> dict:
        self._exigir("cupom:criar", solicitante)
        from datetime import date as dt
        if self._repo.buscar_por_codigo(dados["codigo"]):
            raise ValueError(f"Cupom com código '{dados['codigo']}' já existe.")
        cupom = Cupom(
            codigo=dados["codigo"],
            descricao=dados["descricao"],
            tipo_desconto=TipoDesconto(dados["tipo_desconto"]),
            valor_desconto=dados["valor_desconto"],
            valor_minimo_pedido=dados.get("valor_minimo_pedido", 0),
            usos_maximos=dados.get("usos_maximos", 999),
            valido_de=dt.fromisoformat(dados["valido_de"]),
            valido_ate=dt.fromisoformat(dados["valido_ate"]),
        )
        self._repo.salvar(cupom)
        return cupom.para_dict()

    def editar(self, solicitante: UsuarioBase, cupom_id: str, dados: dict) -> dict:
        self._exigir("cupom:editar", solicitante)
        from datetime import date as dt
        cupom = self._repo.buscar_por_id(cupom_id)
        if not cupom:
            raise ValueError("Cupom não encontrado.")
        cupom.atualizar(
            descricao=dados.get("descricao"),
            valor_desconto=dados.get("valor_desconto"),
            valor_minimo_pedido=dados.get("valor_minimo_pedido"),
            usos_maximos=dados.get("usos_maximos"),
            valido_ate=dt.fromisoformat(dados["valido_ate"]) if "valido_ate" in dados else None,
            ativo=dados.get("ativo"),
        )
        self._repo.salvar(cupom)
        return cupom.para_dict()

    def remover(self, solicitante: UsuarioBase, cupom_id: str) -> bool:
        self._exigir("cupom:remover", solicitante)
        return self._repo.remover(cupom_id)

    @staticmethod
    def _exigir(permissao: str, usuario: UsuarioBase):
        if not usuario.tem_permissao(permissao):
            raise PermissionError(
                f"Usuário '{usuario.login}' não tem permissão: {permissao}"
            )


# ─────────────────────────────────────────────────────────────
# VENDAS
# ─────────────────────────────────────────────────────────────

class ServicoVenda:
    """
    Orquestra o processo de venda:
      1. Verifica permissão
      2. Valida disponibilidade de estoque
      3. Aplica cupom (se houver)
      4. Confirma pedido
      5. Baixa estoque (FEFO)
      6. Persiste tudo
    """

    def __init__(self):
        self._repo_pedido = RepositorioPedido()
        self._repo_bebida = RepositorioBebida()
        self._repo_estoque = RepositorioEstoque()
        self._repo_cupom = RepositorioCupom()

    def realizar_venda(self, solicitante: UsuarioBase, dados: dict) -> dict:
        self._exigir("venda:realizar", solicitante)

        tipo_venda = TipoVenda(dados.get("tipo_venda", "individual"))
        pedido = Pedido(usuario_id=solicitante.id, tipo_venda=tipo_venda)

        # — Monta itens e valida estoque —
        for item_d in dados["itens"]:
            bebida = self._repo_bebida.buscar_por_id(item_d["bebida_id"])
            if not bebida:
                raise ValueError(f"Bebida '{item_d['bebida_id']}' não encontrada.")

            estoque = self._repo_estoque.buscar_estoque_bebida(bebida.id)
            qtd = item_d["quantidade"]
            if estoque.quantidade_disponivel < qtd:
                raise ValueError(
                    f"Estoque insuficiente para '{bebida.nome}'. "
                    f"Disponível: {estoque.quantidade_disponivel}, Solicitado: {qtd}"
                )

            pedido.adicionar_item(ItemPedido(
                bebida_id=bebida.id,
                nome_bebida=bebida.nome,
                quantidade=qtd,
                preco_unitario=bebida.preco.valor,
            ))

        # — Aplica cupom (opcional) —
        codigo_cupom = dados.get("cupom_codigo")
        if codigo_cupom:
            cupom = self._repo_cupom.buscar_por_codigo(codigo_cupom)
            if not cupom:
                raise ValueError(f"Cupom '{codigo_cupom}' não encontrado.")
            pedido.aplicar_cupom(cupom)

        # — Confirma e baixa estoque —
        pedido.confirmar()

        for item_d in dados["itens"]:
            estoque = self._repo_estoque.buscar_estoque_bebida(item_d["bebida_id"])
            estoque.baixar(item_d["quantidade"])
            # Persiste lotes atualizados
            for lote in self._repo_estoque.listar_lotes(item_d["bebida_id"]):
                self._repo_estoque.salvar_lote(lote)
            self._repo_estoque.atualizar_estoque_resumo(item_d["bebida_id"], estoque)
            self._repo_estoque.registrar_movimentacao(
                bebida_id=item_d["bebida_id"],
                quantidade=item_d["quantidade"],
                tipo="saida_venda",
                pedido_id=pedido.id,
            )

        # — Persiste cupom atualizado (usos) e pedido —
        if codigo_cupom:
            cupom_atualizado = self._repo_cupom.buscar_por_codigo(codigo_cupom)
            if cupom_atualizado:
                self._repo_cupom.salvar(cupom_atualizado)

        self._repo_pedido.salvar(pedido)
        return pedido.para_dict()

    def listar(self, solicitante: UsuarioBase) -> list[dict]:
        self._exigir("venda:listar", solicitante)
        return self._repo_pedido.listar()

    @staticmethod
    def _exigir(permissao: str, usuario: UsuarioBase):
        if not usuario.tem_permissao(permissao):
            raise PermissionError(
                f"Usuário '{usuario.login}' não tem permissão: {permissao}"
            )
