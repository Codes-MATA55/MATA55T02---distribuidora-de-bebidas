"""
=============================================================
SERVIÇOS DE APLICAÇÃO — Casos de uso do sistema
=============================================================
Orquestram o domínio sem conter regras de negócio.
Referência: Evans DDD p.106 — Application Service
=============================================================
"""

from datetime import datetime

from apps.dominio import (
    Bebida, CategoriaBebida, ItemPedido, Lote,
    Pedido, UsuarioBase, criar_usuario, MotivoPedido, StatusPedido
)
from .repositorios import (
    RepositorioBebida, RepositorioCategoria,
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
# SERVIÇO DE PEDIDOS / REQUISIÇÕES INTERNAS
# ─────────────────────────────────────────────────────────────

class ServicoPedido:
    """
    Serviço de Aplicação: Orquestra os casos de uso de movimentação interna.
    Não possui regras de negócio, apenas coordena o Domínio e os Repositórios.
    """

    def __init__(self):
        self._repo_pedido = RepositorioPedido()
        self._repo_estoque = RepositorioEstoque()
        self._repo_bebida = RepositorioBebida()

    def _exigir(self, permissao: str, usuario: UsuarioBase):
        """Verifica se o usuário logado tem direitos para a ação."""
        if not usuario.tem_permissao(permissao):
            raise PermissionError(f"Usuário {usuario.login} não tem permissão para: {permissao}")

    def criar_requisicao(self, solicitante: UsuarioBase, dados: dict) -> dict:
        """
        Caso de Uso: Cria um pedido de retirada e dá baixa física nos lotes de estoque.
        """

        self._exigir("pedido:criar", solicitante)

        # 1. Instancia a entidade de Pedido com o novo Enum de Motivo
        pedido = Pedido(
            usuario_id=solicitante.id,
            motivo=MotivoPedido(dados["motivo"])
        )

        # 2. Constrói os itens validando as regras básicas de OO
        for item_d in dados["itens"]:
            bebida = self._repo_bebida.buscar_por_id(item_d["bebida_id"])
            if not bebida:
                raise ValueError(f"Bebida com ID {item_d['bebida_id']} não encontrada.")

            item = ItemPedido(
                bebida_id=item_d["bebida_id"],
                nome_bebida=bebida.nome,
                quantidade=int(item_d["quantidade"])
            )

            pedido.adicionar_item(item)

        # 3. Altera o status do pedido e executa a baixa real nos lotes de estoque
        pedido.confirmar()

        for item_d in dados["itens"]:
            estoque = self._repo_estoque.buscar_estoque_bebida(item_d["bebida_id"])
            
            # O próprio objeto estoque reduz as quantidades respeitando as validades (FEFO)
            estoque.baixar(item_d["quantidade"])
            
            # Atualiza os lotes modificados de volta no arquivo JSON
            for lote in self._repo_estoque.listar_lotes(item_d["bebida_id"]):
                self._repo_estoque.salvar_lote(lote)
                
            self._repo_estoque.atualizar_estoque_resumo(item_d["bebida_id"], estoque)
            
            # Registra no histórico de movimentações o motivo dinâmico da saída
            self._repo_estoque.registrar_movimentacao(
                bebida_id=item_d["bebida_id"],
                quantidade=item_d["quantidade"],
                tipo=f"saida_{pedido.motivo.value}",
                pedido_id=pedido.id,
            )

        # 4. Salva o documento da requisição finalizado
        self._repo_pedido.salvar(pedido)
        return pedido.para_dict()

    def listar(self, solicitante: UsuarioBase) -> list[dict]:
        self._exigir("pedido:listar", solicitante)

        # Admins e Gerentes visualizam todas as movimentações do sistema
        if solicitante.tipo.value in ["administrador", "gerencia"]:
            pedidos = self._repo_pedido.listar()
            return [p.para_dict() for p in pedidos]

        # Usuários comuns veem apenas suas próprias requisições
        pedidos = self._repo_pedido.listar(solicitante_id=solicitante.id)
        return [p.para_dict() for p in pedidos]
    
    def cancelar_requisicao(self, solicitante: UsuarioBase, pedido_id: str) -> dict:
        """
        Caso de Uso: Cancela uma requisição interna de movimentação.
        Utiliza as regras da entidade para transicionar o StatusPedido.
        """
        self._exigir("pedido:cancelar", solicitante)

        # Busca o pedido no repositório (ajuste o método de busca se necessário)
        pedido = self._repo_pedido.buscar_por_id(pedido_id)
        if not pedido:
            raise ValueError("Pedido não encontrado.")

        # A própria entidade valida o estado interno usando StatusPedido
        pedido.cancelar()

        # Persiste a alteração do status
        self._repo_pedido.salvar(pedido)
        return pedido.para_dict()