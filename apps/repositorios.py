"""
=============================================================
REPOSITÓRIOS — Camada de persistência mockada em JSON
=============================================================
Implementa o padrão Repository do DDD:
  - Isola o domínio da infraestrutura (JSON no lugar de banco)
  - O domínio não sabe que os dados vêm de um arquivo
  - Troca por banco real exige mudar apenas esta camada

Referência: Evans DDD p.138 | Fowler PEAA p.347
=============================================================
"""

import json
import os
import threading
from datetime import date, datetime
from typing import Optional

from .dominio import (
    Bebida, CategoriaBebida, Estoque, Lote,
    Pedido, ItemPedido, StatusPedido, MotivoPedido,
    UsuarioBase, criar_usuario
)

# Caminho do arquivo JSON (configurável via variável de ambiente)
DB_PATH = os.environ.get(
    "DB_JSON_PATH",
    os.path.join(os.path.dirname(__file__), "..", "data", "db.json"),
)

# Lock para evitar race condition em escritas concorrentes
_lock = threading.Lock()


# ─────────────────────────────────────────────────────────────
# UTILITÁRIOS DE I/O
# ─────────────────────────────────────────────────────────────

def _ler_db() -> dict:
    with open(DB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _salvar_db(db: dict):
    with _lock:
        with open(DB_PATH, "w", encoding="utf-8") as f:
            json.dump(db, f, ensure_ascii=False, indent=2)


# ─────────────────────────────────────────────────────────────
# REPOSITÓRIO DE USUÁRIOS
# ─────────────────────────────────────────────────────────────

class RepositorioUsuario:
    """Abstrai operações de leitura/escrita de usuários no JSON."""

    @staticmethod
    def _dict_para_usuario(d: dict) -> UsuarioBase:
        return criar_usuario(
            tipo=d["tipo"],
            id=d["id"],
            nome=d["nome"],
            login=d["login"],
            senha_uid=d["senha_uid"],
            ativo=d.get("ativo", True),
            criado_em=datetime.fromisoformat(d["criado_em"]),
        )

    def buscar_por_login(self, login: str) -> Optional[UsuarioBase]:
        db = _ler_db()
        for u in db["usuarios"]:
            if u["login"] == login:
                return self._dict_para_usuario(u)
        return None

    def buscar_por_id(self, id: str) -> Optional[UsuarioBase]:
        db = _ler_db()
        for u in db["usuarios"]:
            if u["id"] == id:
                return self._dict_para_usuario(u)
        return None

    def listar(self) -> list[UsuarioBase]:
        db = _ler_db()
        return [self._dict_para_usuario(u) for u in db["usuarios"]]

    def salvar(self, usuario: UsuarioBase):
        db = _ler_db()
        dados = usuario.para_dict()
        # Preserva senha_uid que não é exposta no para_dict
        for u in db["usuarios"]:
            if u["id"] == usuario.id:
                u.update(dados)
                _salvar_db(db)
                return
        # Novo usuário — senha precisa ser passada separadamente
        db["usuarios"].append(dados)
        _salvar_db(db)

    def salvar_novo(self, usuario: UsuarioBase, senha_uid: str):
        db = _ler_db()
        dados = usuario.para_dict()
        dados["senha_uid"] = senha_uid
        db["usuarios"].append(dados)
        _salvar_db(db)

    def atualizar_senha(self, usuario_id: str, nova_senha: str) -> bool:
        db = _ler_db()
        for u in db["usuarios"]:
            if u["id"] == usuario_id:
                u["senha_uid"] = nova_senha
                _salvar_db(db)
                return True
        return False

    def remover(self, id: str) -> bool:
        db = _ler_db()
        antes = len(db["usuarios"])
        db["usuarios"] = [u for u in db["usuarios"] if u["id"] != id]
        if len(db["usuarios"]) < antes:
            _salvar_db(db)
            return True
        return False


# ─────────────────────────────────────────────────────────────
# REPOSITÓRIO DE CATEGORIAS
# ─────────────────────────────────────────────────────────────

class RepositorioCategoria:

    @staticmethod
    def _dict_para_categoria(d: dict) -> CategoriaBebida:
        return CategoriaBebida(
            id=d["id"],
            nome=d["nome"],
            descricao=d["descricao"],
            alcoolica=d["alcoolica"],
            criado_em=datetime.fromisoformat(d["criado_em"]),
        )

    def listar(self) -> list[CategoriaBebida]:
        db = _ler_db()
        return [self._dict_para_categoria(c) for c in db["categorias_bebida"]]

    def buscar_por_id(self, id: str) -> Optional[CategoriaBebida]:
        db = _ler_db()
        for c in db["categorias_bebida"]:
            if c["id"] == id:
                return self._dict_para_categoria(c)
        return None

    def salvar(self, categoria: CategoriaBebida):
        db = _ler_db()
        dados = categoria.para_dict()
        for c in db["categorias_bebida"]:
            if c["id"] == categoria.id:
                c.update(dados)
                _salvar_db(db)
                return
        db["categorias_bebida"].append(dados)
        _salvar_db(db)

    def remover(self, id: str) -> bool:
        db = _ler_db()
        antes = len(db["categorias_bebida"])
        db["categorias_bebida"] = [c for c in db["categorias_bebida"] if c["id"] != id]
        if len(db["categorias_bebida"]) < antes:
            _salvar_db(db)
            return True
        return False


# ─────────────────────────────────────────────────────────────
# REPOSITÓRIO DE BEBIDAS
# ─────────────────────────────────────────────────────────────

class RepositorioBebida:

    @staticmethod
    def _dict_para_bebida(d: dict) -> Bebida:
        return Bebida(
            id=d["id"],
            nome=d["nome"],
            categoria_id=d["categoria_id"],
            marca=d["marca"],
            volume_ml=d["volume_ml"],
            teor_alcoolico=d.get("teor_alcoolico"),
            fornecedor=d["fornecedor"],
            ativo=d.get("ativo", True),
            criado_em=datetime.fromisoformat(d["criado_em"]),
            atualizado_em=datetime.fromisoformat(d["atualizado_em"]),
        )

    def listar(self, apenas_ativos: bool = True) -> list[Bebida]:
        db = _ler_db()
        bebidas = [self._dict_para_bebida(b) for b in db["bebidas"]]
        if apenas_ativos:
            bebidas = [b for b in bebidas if b.ativo]
        return bebidas

    def buscar_por_id(self, id: str) -> Optional[Bebida]:
        db = _ler_db()
        for b in db["bebidas"]:
            if b["id"] == id:
                return self._dict_para_bebida(b)
        return None

    def salvar(self, bebida: Bebida):
        db = _ler_db()
        dados = bebida.para_dict()
        for b in db["bebidas"]:
            if b["id"] == bebida.id:
                b.update(dados)
                _salvar_db(db)
                return
        db["bebidas"].append(dados)
        _salvar_db(db)

    def remover(self, id: str) -> bool:
        """Remoção lógica via desativar() no domínio."""
        bebida = self.buscar_por_id(id)
        if not bebida:
            return False
        bebida.desativar()
        self.salvar(bebida)
        return True


# ─────────────────────────────────────────────────────────────
# REPOSITÓRIO DE LOTES / ESTOQUE
# ─────────────────────────────────────────────────────────────

class RepositorioEstoque:

    @staticmethod
    def _dict_para_lote(d: dict) -> Lote:
        return Lote(
            id=d["id"],
            bebida_id=d["bebida_id"],
            quantidade=d["quantidade"],
            quantidade_disponivel=d.get("quantidade_disponivel", d["quantidade"]),
            data_fabricacao=date.fromisoformat(d["data_fabricacao"]),
            data_validade=date.fromisoformat(d["data_validade"]),
            codigo_lote=d["codigo_lote"],
            criado_em=datetime.fromisoformat(d["criado_em"]),
        )

    def buscar_estoque_bebida(self, bebida_id: str) -> Estoque:
        db = _ler_db()
        resumo = next((e for e in db["estoque"] if e["bebida_id"] == bebida_id), None)
        quantidade_reservada = resumo.get("quantidade_reservada", 0) if resumo else 0

        estoque = Estoque(bebida_id, quantidade_reservada=quantidade_reservada)
        for l in db["lotes"]:
            if l["bebida_id"] == bebida_id:
                estoque.adicionar_lote(self._dict_para_lote(l))
        return estoque

    def listar_lotes(self, bebida_id: str = None) -> list[Lote]:
        db = _ler_db()
        lotes = db["lotes"]
        if bebida_id:
            lotes = [l for l in lotes if l["bebida_id"] == bebida_id]
        return [self._dict_para_lote(l) for l in lotes]

    def salvar_lote(self, lote: Lote):
        db = _ler_db()
        dados = lote.para_dict()
        for l in db["lotes"]:
            if l["id"] == lote.id:
                l.update(dados)
                _salvar_db(db)
                return
        db["lotes"].append(dados)
        _salvar_db(db)

    def remover_lote(self, id: str) -> bool:
        db = _ler_db()
        antes = len(db["lotes"])
        db["lotes"] = [l for l in db["lotes"] if l["id"] != id]
        if len(db["lotes"]) < antes:
            _salvar_db(db)
            return True
        return False

    def atualizar_estoque_resumo(self, bebida_id: str, estoque: Estoque):
        db = _ler_db()
        dados = estoque.para_dict()
        for e in db["estoque"]:
            if e["bebida_id"] == bebida_id:
                e.update(dados)
                _salvar_db(db)
                return
        db["estoque"].append(dados)
        _salvar_db(db)

    def registrar_movimentacao(self, bebida_id: str, quantidade: int, tipo: str, pedido_id: str = None):
        db = _ler_db()
        mov = {
            "id": f"mov-{datetime.now().strftime('%Y%m%d%H%M%S%f')}",
            "bebida_id": bebida_id,
            "quantidade": quantidade,
            "tipo": tipo,
            "pedido_id": pedido_id,
            "criado_em": datetime.now().isoformat(),
        }
        db["movimentacoes_estoque"].append(mov)
        _salvar_db(db)



# ─────────────────────────────────────────────────────────────
# REPOSITÓRIO DE PEDIDOS
# ─────────────────────────────────────────────────────────────


class RepositorioPedido:

    @staticmethod
    def _dict_para_pedido(dados: dict) -> Pedido:
        itens = [ItemPedido(**item_dict) for item_dict in dados.get("itens", [])]
        return Pedido.reconstruir(
            usuario_id=dados["usuario_id"],
            motivo=MotivoPedido(dados["motivo"]),
            id=dados["id"],
            criado_em=datetime.fromisoformat(dados["criado_em"]),
            status=StatusPedido(dados["status"]),
            itens=itens,
        )

    def listar(self, usuario_id: str = None) -> list[Pedido]:
        """Lista todas as requisições (com opção de filtrar por usuário)."""
        db = _ler_db()
        pedidos = db["pedidos"]
        if usuario_id:
            pedidos = [p for p in pedidos if p["usuario_id"] == usuario_id]
        return [self._dict_para_pedido(p) for p in pedidos]

    def buscar_por_id(self, id: str) -> Optional[Pedido]:
        db = _ler_db()
        for p in db["pedidos"]:
            if p["id"] == id:
                return self._dict_para_pedido(p)
        return None

    def salvar(self, pedido: Pedido):
        """Insere ou atualiza um pedido no banco de dados falso (JSON)."""
        db = _ler_db()
        
        # Procura se o pedido já existe para atualizar
        ind = -1
        for i, p in enumerate(db["pedidos"]):
            if p["id"] == pedido.id:
                ind = i
                break

        pedido_dict = pedido.para_dict()

        if ind >= 0:
            db["pedidos"][ind] = pedido_dict  # Atualiza
        else:
            db["pedidos"].append(pedido_dict) # Cria novo

        _salvar_db(db)