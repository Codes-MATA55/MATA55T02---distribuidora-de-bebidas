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
    Bebida, CategoriaBebida, Cupom, Estoque, Lote,
    Pedido, ItemPedido, TipoDesconto, TipoVenda, StatusPedido,
    UsuarioBase, criar_usuario,
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
            preco_unitario=d["preco_unitario"],
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
        estoque = Estoque(bebida_id)
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
# REPOSITÓRIO DE CUPONS
# ─────────────────────────────────────────────────────────────

class RepositorioCupom:

    @staticmethod
    def _dict_para_cupom(d: dict) -> Cupom:
        return Cupom(
            id=d["id"],
            codigo=d["codigo"],
            descricao=d["descricao"],
            tipo_desconto=TipoDesconto(d["tipo_desconto"]),
            valor_desconto=d["valor_desconto"],
            valor_minimo_pedido=d["valor_minimo_pedido"],
            usos_maximos=d["usos_maximos"],
            usos_realizados=d.get("usos_realizados", 0),
            ativo=d.get("ativo", True),
            valido_de=date.fromisoformat(d["valido_de"]),
            valido_ate=date.fromisoformat(d["valido_ate"]),
            criado_em=datetime.fromisoformat(d["criado_em"]),
        )

    def listar(self, apenas_ativos: bool = False) -> list[Cupom]:
        db = _ler_db()
        cupons = [self._dict_para_cupom(c) for c in db["cupons"]]
        if apenas_ativos:
            cupons = [c for c in cupons if c.ativo]
        return cupons

    def buscar_por_codigo(self, codigo: str) -> Optional[Cupom]:
        db = _ler_db()
        codigo_upper = codigo.strip().upper()
        for c in db["cupons"]:
            if c["codigo"] == codigo_upper:
                return self._dict_para_cupom(c)
        return None

    def buscar_por_id(self, id: str) -> Optional[Cupom]:
        db = _ler_db()
        for c in db["cupons"]:
            if c["id"] == id:
                return self._dict_para_cupom(c)
        return None

    def salvar(self, cupom: Cupom):
        db = _ler_db()
        dados = cupom.para_dict()
        for c in db["cupons"]:
            if c["id"] == cupom.id:
                c.update(dados)
                _salvar_db(db)
                return
        db["cupons"].append(dados)
        _salvar_db(db)

    def remover(self, id: str) -> bool:
        cupom = self.buscar_por_id(id)
        if not cupom:
            return False
        cupom.desativar()
        self.salvar(cupom)
        return True


# ─────────────────────────────────────────────────────────────
# REPOSITÓRIO DE PEDIDOS
# ─────────────────────────────────────────────────────────────

class RepositorioPedido:

    @staticmethod
    def _dict_para_pedido(d: dict) -> Pedido:
        pedido = Pedido(
            id=d["id"],
            usuario_id=d["usuario_id"],
            tipo_venda=TipoVenda(d["tipo_venda"]),
            criado_em=datetime.fromisoformat(d["criado_em"]),
        )
        for item_d in d.get("itens", []):
            pedido.adicionar_item(ItemPedido(
                bebida_id=item_d["bebida_id"],
                nome_bebida=item_d["nome_bebida"],
                quantidade=item_d["quantidade"],
                preco_unitario=item_d["preco_unitario"],
            ))
        return pedido

    def listar(self, usuario_id: str = None) -> list[dict]:
        db = _ler_db()
        pedidos = db["pedidos"]
        if usuario_id:
            pedidos = [p for p in pedidos if p["usuario_id"] == usuario_id]
        return pedidos

    def buscar_por_id(self, id: str) -> Optional[dict]:
        db = _ler_db()
        for p in db["pedidos"]:
            if p["id"] == id:
                return p
        return None

    def salvar(self, pedido: Pedido):
        db = _ler_db()
        dados = pedido.para_dict()
        for p in db["pedidos"]:
            if p["id"] == pedido.id:
                p.update(dados)
                _salvar_db(db)
                return
        db["pedidos"].append(dados)
        _salvar_db(db)
