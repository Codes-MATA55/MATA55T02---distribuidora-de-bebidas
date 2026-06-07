"""
=============================================================
VIEWS (Controllers MVC) — Django REST sem DRF
=============================================================
Cada view:
  1. Extrai o usuário autenticado do token no header
  2. Chama o Serviço de Aplicação correspondente
  3. Devolve JsonResponse

Padrão MVC:
  Model  → dominio.py + repositorios.py
  View   → templates (não usados; API pura)
  Controller → este arquivo (views.py)
=============================================================
"""

import json
import jwt
import os
from functools import wraps
from datetime import datetime, timedelta

from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

from apps.servicos import (
    ServicoAutenticacao,
    ServicoBebida,
    ServicoCategoria,
    ServicoCupom,
    ServicoEstoque,
    ServicoUsuario,
    ServicoVenda,
)

JWT_SECRET = os.environ.get("JWT_SECRET", "distribuidora-secret-poo-2026")
JWT_ALGO   = "HS256"
JWT_EXP_H  = 8  # horas


# ─────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────

def _gerar_token(usuario_id: str, tipo: str) -> str:
    payload = {
        "sub": usuario_id,
        "tipo": tipo,
        "exp": datetime.utcnow() + timedelta(hours=JWT_EXP_H),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGO)


def _extrair_usuario_id(request) -> str | None:
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    token = auth.split(" ", 1)[1]
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGO])
        return payload.get("sub")
    except jwt.PyJWTError:
        return None


def _sucesso(data, status=200) -> JsonResponse:
    return JsonResponse({"ok": True, "data": data}, status=status)


def _erro(mensagem: str, status=400) -> JsonResponse:
    return JsonResponse({"ok": False, "erro": mensagem}, status=status)


def _body(request) -> dict:
    try:
        return json.loads(request.body or "{}")
    except json.JSONDecodeError:
        return {}


# ─────────────────────────────────────────────────────────────
# DECORATOR — exige autenticação
# ─────────────────────────────────────────────────────────────

def requer_autenticacao(func):
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        usuario_id = _extrair_usuario_id(request)
        if not usuario_id:
            return _erro("Token ausente ou inválido.", status=401)
        try:
            svc = ServicoAutenticacao()
            request.usuario = svc.obter_usuario(usuario_id)
        except ValueError:
            return _erro("Usuário não encontrado.", status=401)
        return func(request, *args, **kwargs)
    return wrapper


# ─────────────────────────────────────────────────────────────
# AUTH
# ─────────────────────────────────────────────────────────────

@csrf_exempt
@require_http_methods(["POST"])
def login(request):
    """
    POST /api/auth/login/
    Body: { "login": "...", "senha_uid": "..." }
    """
    dados = _body(request)
    login_val = dados.get("login", "")
    senha_uid = dados.get("senha_uid", "")
    if not login_val or not senha_uid:
        return _erro("Campos 'login' e 'senha_uid' são obrigatórios.")
    try:
        svc = ServicoAutenticacao()
        usuario = svc.autenticar(login_val, senha_uid)
        token = _gerar_token(usuario.id, usuario.tipo.value)
        return _sucesso({
            "token": token,
            "usuario": usuario.para_dict(),
        })
    except PermissionError as e:
        return _erro(str(e), status=401)


@csrf_exempt
@require_http_methods(["GET"])
@requer_autenticacao
def perfil(request):
    """GET /api/auth/perfil/ — retorna dados do usuário logado."""
    return _sucesso(request.usuario.para_dict())


# ─────────────────────────────────────────────────────────────
# USUÁRIOS
# ─────────────────────────────────────────────────────────────

@csrf_exempt
@requer_autenticacao
def usuarios(request):
    """
    GET  /api/usuarios/  — lista usuários
    POST /api/usuarios/  — cria usuário
    """
    svc = ServicoUsuario()
    try:
        if request.method == "GET":
            return _sucesso(svc.listar(request.usuario))
        if request.method == "POST":
            dados = _body(request)
            return _sucesso(svc.criar(request.usuario, dados), status=201)
    except PermissionError as e:
        return _erro(str(e), status=403)
    except ValueError as e:
        return _erro(str(e))


@csrf_exempt
@requer_autenticacao
def usuario_detalhe(request, usuario_id):
    """PUT / DELETE /api/usuarios/<id>/"""
    svc = ServicoUsuario()
    try:
        if request.method == "PUT":
            return _sucesso(svc.editar(request.usuario, usuario_id, _body(request)))
        if request.method == "DELETE":
            removido = svc.remover(request.usuario, usuario_id)
            return _sucesso({"removido": removido})
    except PermissionError as e:
        return _erro(str(e), status=403)
    except ValueError as e:
        return _erro(str(e))
    return _erro("Método não permitido.", status=405)


# ─────────────────────────────────────────────────────────────
# CATEGORIAS
# ─────────────────────────────────────────────────────────────

@csrf_exempt
@requer_autenticacao
def categorias(request):
    """GET / POST /api/categorias/"""
    svc = ServicoCategoria()
    try:
        if request.method == "GET":
            return _sucesso(svc.listar(request.usuario))
        if request.method == "POST":
            return _sucesso(svc.criar(request.usuario, _body(request)), status=201)
    except PermissionError as e:
        return _erro(str(e), status=403)
    except ValueError as e:
        return _erro(str(e))


@csrf_exempt
@requer_autenticacao
def categoria_detalhe(request, categoria_id):
    """PUT / DELETE /api/categorias/<id>/"""
    svc = ServicoCategoria()
    try:
        if request.method == "PUT":
            return _sucesso(svc.editar(request.usuario, categoria_id, _body(request)))
        if request.method == "DELETE":
            return _sucesso({"removido": svc.remover(request.usuario, categoria_id)})
    except PermissionError as e:
        return _erro(str(e), status=403)
    except ValueError as e:
        return _erro(str(e))
    return _erro("Método não permitido.", status=405)


# ─────────────────────────────────────────────────────────────
# BEBIDAS
# ─────────────────────────────────────────────────────────────

@csrf_exempt
@requer_autenticacao
def bebidas(request):
    """GET / POST /api/bebidas/"""
    svc = ServicoBebida()
    try:
        if request.method == "GET":
            return _sucesso(svc.listar(request.usuario))
        if request.method == "POST":
            return _sucesso(svc.criar(request.usuario, _body(request)), status=201)
    except PermissionError as e:
        return _erro(str(e), status=403)
    except ValueError as e:
        return _erro(str(e))


@csrf_exempt
@requer_autenticacao
def bebida_detalhe(request, bebida_id):
    """PUT / DELETE /api/bebidas/<id>/"""
    svc = ServicoBebida()
    try:
        if request.method == "PUT":
            return _sucesso(svc.editar(request.usuario, bebida_id, _body(request)))
        if request.method == "DELETE":
            return _sucesso({"removido": svc.remover(request.usuario, bebida_id)})
    except PermissionError as e:
        return _erro(str(e), status=403)
    except ValueError as e:
        return _erro(str(e))
    return _erro("Método não permitido.", status=405)


# ─────────────────────────────────────────────────────────────
# ESTOQUE
# ─────────────────────────────────────────────────────────────

@csrf_exempt
@requer_autenticacao
def estoque(request):
    """GET /api/estoque/ — lista estoque de todas as bebidas"""
    svc = ServicoEstoque()
    try:
        return _sucesso(svc.listar(request.usuario))
    except PermissionError as e:
        return _erro(str(e), status=403)


@csrf_exempt
@requer_autenticacao
def estoque_lotes(request):
    """POST /api/estoque/lotes/ — adiciona lote"""
    svc = ServicoEstoque()
    try:
        if request.method == "POST":
            return _sucesso(svc.adicionar_lote(request.usuario, _body(request)), status=201)
    except PermissionError as e:
        return _erro(str(e), status=403)
    except ValueError as e:
        return _erro(str(e))
    return _erro("Método não permitido.", status=405)


@csrf_exempt
@requer_autenticacao
def estoque_lote_detalhe(request, lote_id):
    """PUT / DELETE /api/estoque/lotes/<id>/"""
    svc = ServicoEstoque()
    try:
        if request.method == "PUT":
            return _sucesso(svc.editar_lote(request.usuario, lote_id, _body(request)))
        if request.method == "DELETE":
            return _sucesso({"removido": svc.remover_lote(request.usuario, lote_id)})
    except PermissionError as e:
        return _erro(str(e), status=403)
    except ValueError as e:
        return _erro(str(e))
    return _erro("Método não permitido.", status=405)


# ─────────────────────────────────────────────────────────────
# CUPONS
# ─────────────────────────────────────────────────────────────

@csrf_exempt
@requer_autenticacao
def cupons(request):
    """GET / POST /api/cupons/"""
    svc = ServicoCupom()
    try:
        if request.method == "GET":
            return _sucesso(svc.listar(request.usuario))
        if request.method == "POST":
            return _sucesso(svc.criar(request.usuario, _body(request)), status=201)
    except PermissionError as e:
        return _erro(str(e), status=403)
    except ValueError as e:
        return _erro(str(e))


@csrf_exempt
@requer_autenticacao
def cupom_detalhe(request, cupom_id):
    """PUT / DELETE /api/cupons/<id>/"""
    svc = ServicoCupom()
    try:
        if request.method == "PUT":
            return _sucesso(svc.editar(request.usuario, cupom_id, _body(request)))
        if request.method == "DELETE":
            return _sucesso({"removido": svc.remover(request.usuario, cupom_id)})
    except PermissionError as e:
        return _erro(str(e), status=403)
    except ValueError as e:
        return _erro(str(e))
    return _erro("Método não permitido.", status=405)


# ─────────────────────────────────────────────────────────────
# VENDAS
# ─────────────────────────────────────────────────────────────

@csrf_exempt
@requer_autenticacao
def vendas(request):
    """
    GET  /api/vendas/  — lista pedidos
    POST /api/vendas/  — realiza venda

    Body POST (individual):
    {
      "tipo_venda": "individual",
      "itens": [
        { "bebida_id": "beb-001", "quantidade": 5 }
      ],
      "cupom_codigo": "PROMO10"   <- opcional
    }

    Body POST (lote):
    {
      "tipo_venda": "lote",
      "itens": [
        { "bebida_id": "beb-001", "quantidade": 1000 },
        { "bebida_id": "beb-002", "quantidade": 200 }
      ]
    }
    """
    svc = ServicoVenda()
    try:
        if request.method == "GET":
            return _sucesso(svc.listar(request.usuario))
        if request.method == "POST":
            return _sucesso(svc.realizar_venda(request.usuario, _body(request)), status=201)
    except PermissionError as e:
        return _erro(str(e), status=403)
    except ValueError as e:
        return _erro(str(e))


# ─────────────────────────────────────────────────────────────
# SWAGGER / OPENAPI
# ─────────────────────────────────────────────────────────────

_OPENAPI_SPEC = {
    "openapi": "3.0.3",
    "info": {
        "title": "Distribuidora de Bebidas",
        "version": "1.0.0",
        "description": "API REST para gerenciamento de distribuidora de bebidas em alta escala.",
    },
    "servers": [{"url": "http://localhost:8000"}],
    "components": {
        "securitySchemes": {
            "bearerAuth": {"type": "http", "scheme": "bearer", "bearerFormat": "JWT"}
        },
        "schemas": {
            "Ok": {
                "type": "object",
                "properties": {
                    "ok": {"type": "boolean", "example": True},
                    "data": {},
                },
            },
            "Erro": {
                "type": "object",
                "properties": {
                    "ok": {"type": "boolean", "example": False},
                    "erro": {"type": "string"},
                },
            },
            "LoginInput": {
                "type": "object",
                "required": ["login", "senha_uid"],
                "properties": {
                    "login": {"type": "string", "example": "admin"},
                    "senha_uid": {"type": "string", "example": "uid-admin-001"},
                },
            },
            "UsuarioInput": {
                "type": "object",
                "required": ["nome", "login", "senha_uid", "tipo"],
                "properties": {
                    "nome": {"type": "string", "example": "Maria Silva"},
                    "login": {"type": "string", "example": "maria"},
                    "senha_uid": {"type": "string", "example": "uid-maria-001"},
                    "tipo": {"type": "string", "enum": ["administrador", "gerencia", "vendas", "estoque"]},
                },
            },
            "CategoriaInput": {
                "type": "object",
                "required": ["nome"],
                "properties": {
                    "nome": {"type": "string", "example": "Cervejas"},
                    "descricao": {"type": "string", "example": "Cervejas nacionais e importadas"},
                    "alcoolica": {"type": "boolean", "example": True},
                },
            },
            "BebidaInput": {
                "type": "object",
                "required": ["nome", "categoria_id", "marca", "volume_ml", "preco_unitario", "fornecedor"],
                "properties": {
                    "nome": {"type": "string", "example": "Heineken 600ml"},
                    "categoria_id": {"type": "string", "example": "cat-abc123"},
                    "marca": {"type": "string", "example": "Heineken"},
                    "volume_ml": {"type": "integer", "example": 600},
                    "preco_unitario": {"type": "number", "example": 8.50},
                    "teor_alcoolico": {"type": "number", "example": 5.0},
                    "fornecedor": {"type": "string", "example": "Distribuidora XYZ"},
                },
            },
            "LoteInput": {
                "type": "object",
                "required": ["bebida_id", "quantidade", "data_fabricacao", "data_validade", "codigo_lote"],
                "properties": {
                    "bebida_id": {"type": "string", "example": "beb-abc123"},
                    "quantidade": {"type": "integer", "example": 500},
                    "data_fabricacao": {"type": "string", "format": "date", "example": "2024-01-01"},
                    "data_validade": {"type": "string", "format": "date", "example": "2025-01-01"},
                    "codigo_lote": {"type": "string", "example": "LOT-2024-001"},
                },
            },
            "CupomInput": {
                "type": "object",
                "required": ["codigo", "descricao", "tipo_desconto", "valor_desconto", "valido_de", "valido_ate"],
                "properties": {
                    "codigo": {"type": "string", "example": "PROMO10"},
                    "descricao": {"type": "string", "example": "10% de desconto"},
                    "tipo_desconto": {"type": "string", "enum": ["percentual", "fixo"]},
                    "valor_desconto": {"type": "number", "example": 10.0},
                    "valor_minimo_pedido": {"type": "number", "example": 50.0},
                    "usos_maximos": {"type": "integer", "example": 100},
                    "valido_de": {"type": "string", "format": "date", "example": "2026-01-01"},
                    "valido_ate": {"type": "string", "format": "date", "example": "2026-12-31"},
                },
            },
            "ItemPedido": {
                "type": "object",
                "properties": {
                    "bebida_id": {"type": "string"},
                    "nome_bebida": {"type": "string"},
                    "quantidade": {"type": "integer"},
                    "preco_unitario": {"type": "number"},
                    "subtotal": {"type": "number"},
                },
            },
            "VendaInput": {
                "type": "object",
                "required": ["tipo_venda", "itens"],
                "properties": {
                    "tipo_venda": {"type": "string", "enum": ["individual", "lote"], "example": "individual"},
                    "itens": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "required": ["bebida_id", "quantidade"],
                            "properties": {
                                "bebida_id": {"type": "string", "example": "beb-abc123"},
                                "quantidade": {"type": "integer", "example": 5},
                            },
                        },
                    },
                    "cupom_codigo": {"type": "string", "example": "PROMO10"},
                },
            },
        },
    },
    "security": [{"bearerAuth": []}],
    "paths": {
        "/api/auth/login/": {
            "post": {
                "tags": ["Auth"],
                "summary": "Login",
                "description": "Autentica o usuário e retorna um token JWT.",
                "security": [],
                "requestBody": {
                    "required": True,
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/LoginInput"}}},
                },
                "responses": {
                    "200": {"description": "Token JWT gerado com sucesso"},
                    "401": {"description": "Credenciais inválidas"},
                },
            }
        },
        "/api/auth/perfil/": {
            "get": {
                "tags": ["Auth"],
                "summary": "Perfil do usuário logado",
                "responses": {
                    "200": {"description": "Dados do usuário autenticado"},
                    "401": {"description": "Não autenticado"},
                },
            }
        },
        "/api/usuarios/": {
            "get": {
                "tags": ["Usuários"],
                "summary": "Listar usuários",
                "responses": {"200": {"description": "Lista de usuários"}},
            },
            "post": {
                "tags": ["Usuários"],
                "summary": "Criar usuário",
                "requestBody": {
                    "required": True,
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/UsuarioInput"}}},
                },
                "responses": {
                    "201": {"description": "Usuário criado"},
                    "400": {"description": "Dados inválidos ou login já em uso"},
                    "403": {"description": "Sem permissão"},
                },
            },
        },
        "/api/usuarios/{usuario_id}/": {
            "put": {
                "tags": ["Usuários"],
                "summary": "Editar usuário",
                "parameters": [{"name": "usuario_id", "in": "path", "required": True, "schema": {"type": "string"}}],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "nome": {"type": "string", "example": "Maria Silva"},
                                    "tipo": {"type": "string", "enum": ["administrador", "gerencia", "vendas", "estoque"]},
                                    "senha_uid": {"type": "string", "example": "nova-senha-uid"},
                                },
                            }
                        }
                    },
                },
                "responses": {
                    "200": {"description": "Usuário atualizado"},
                    "400": {"description": "Dados inválidos"},
                    "403": {"description": "Sem permissão (apenas Administrador)"},
                },
            },
            "delete": {
                "tags": ["Usuários"],
                "summary": "Remover usuário",
                "parameters": [{"name": "usuario_id", "in": "path", "required": True, "schema": {"type": "string"}}],
                "responses": {
                    "200": {"description": "Usuário removido"},
                    "403": {"description": "Sem permissão"},
                },
            },
        },
        "/api/categorias/": {
            "get": {
                "tags": ["Categorias"],
                "summary": "Listar categorias",
                "responses": {"200": {"description": "Lista de categorias"}},
            },
            "post": {
                "tags": ["Categorias"],
                "summary": "Criar categoria",
                "requestBody": {
                    "required": True,
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/CategoriaInput"}}},
                },
                "responses": {"201": {"description": "Categoria criada"}, "403": {"description": "Sem permissão"}},
            },
        },
        "/api/categorias/{categoria_id}/": {
            "put": {
                "tags": ["Categorias"],
                "summary": "Editar categoria",
                "parameters": [{"name": "categoria_id", "in": "path", "required": True, "schema": {"type": "string"}}],
                "requestBody": {
                    "required": True,
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/CategoriaInput"}}},
                },
                "responses": {"200": {"description": "Categoria atualizada"}, "403": {"description": "Sem permissão"}},
            },
            "delete": {
                "tags": ["Categorias"],
                "summary": "Remover categoria",
                "parameters": [{"name": "categoria_id", "in": "path", "required": True, "schema": {"type": "string"}}],
                "responses": {"200": {"description": "Categoria removida"}, "403": {"description": "Sem permissão"}},
            },
        },
        "/api/bebidas/": {
            "get": {
                "tags": ["Bebidas"],
                "summary": "Listar bebidas",
                "responses": {"200": {"description": "Lista de bebidas"}},
            },
            "post": {
                "tags": ["Bebidas"],
                "summary": "Criar bebida",
                "requestBody": {
                    "required": True,
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/BebidaInput"}}},
                },
                "responses": {"201": {"description": "Bebida criada"}, "403": {"description": "Sem permissão"}},
            },
        },
        "/api/bebidas/{bebida_id}/": {
            "put": {
                "tags": ["Bebidas"],
                "summary": "Editar bebida",
                "parameters": [{"name": "bebida_id", "in": "path", "required": True, "schema": {"type": "string"}}],
                "requestBody": {
                    "required": True,
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/BebidaInput"}}},
                },
                "responses": {"200": {"description": "Bebida atualizada"}, "403": {"description": "Sem permissão"}},
            },
            "delete": {
                "tags": ["Bebidas"],
                "summary": "Remover bebida",
                "parameters": [{"name": "bebida_id", "in": "path", "required": True, "schema": {"type": "string"}}],
                "responses": {"200": {"description": "Bebida removida"}, "403": {"description": "Sem permissão"}},
            },
        },
        "/api/estoque/": {
            "get": {
                "tags": ["Estoque"],
                "summary": "Listar estoque de todas as bebidas",
                "responses": {"200": {"description": "Lista de estoque por bebida"}},
            }
        },
        "/api/estoque/lotes/": {
            "post": {
                "tags": ["Estoque"],
                "summary": "Adicionar lote",
                "requestBody": {
                    "required": True,
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/LoteInput"}}},
                },
                "responses": {"201": {"description": "Lote adicionado"}, "403": {"description": "Sem permissão"}},
            }
        },
        "/api/estoque/lotes/{lote_id}/": {
            "put": {
                "tags": ["Estoque"],
                "summary": "Editar lote",
                "parameters": [{"name": "lote_id", "in": "path", "required": True, "schema": {"type": "string"}}],
                "requestBody": {
                    "required": True,
                    "content": {
                        "application/json": {
                            "schema": {
                                "type": "object",
                                "properties": {
                                    "data_fabricacao": {"type": "string", "format": "date", "example": "2024-01-01"},
                                    "data_validade": {"type": "string", "format": "date", "example": "2025-12-31"},
                                    "codigo_lote": {"type": "string", "example": "LOT-2024-001-REV"},
                                },
                            }
                        }
                    },
                },
                "responses": {
                    "200": {"description": "Lote atualizado"},
                    "400": {"description": "Dados inválidos"},
                    "403": {"description": "Sem permissão"},
                },
            },
            "delete": {
                "tags": ["Estoque"],
                "summary": "Remover lote",
                "parameters": [{"name": "lote_id", "in": "path", "required": True, "schema": {"type": "string"}}],
                "responses": {"200": {"description": "Lote removido"}, "403": {"description": "Sem permissão"}},
            },
        },
        "/api/cupons/": {
            "get": {
                "tags": ["Cupons"],
                "summary": "Listar cupons",
                "responses": {"200": {"description": "Lista de cupons"}},
            },
            "post": {
                "tags": ["Cupons"],
                "summary": "Criar cupom",
                "requestBody": {
                    "required": True,
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/CupomInput"}}},
                },
                "responses": {"201": {"description": "Cupom criado"}, "403": {"description": "Sem permissão"}},
            },
        },
        "/api/cupons/{cupom_id}/": {
            "put": {
                "tags": ["Cupons"],
                "summary": "Editar cupom",
                "parameters": [{"name": "cupom_id", "in": "path", "required": True, "schema": {"type": "string"}}],
                "requestBody": {
                    "required": True,
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/CupomInput"}}},
                },
                "responses": {"200": {"description": "Cupom atualizado"}, "403": {"description": "Sem permissão"}},
            },
            "delete": {
                "tags": ["Cupons"],
                "summary": "Remover cupom",
                "parameters": [{"name": "cupom_id", "in": "path", "required": True, "schema": {"type": "string"}}],
                "responses": {"200": {"description": "Cupom removido"}, "403": {"description": "Sem permissão"}},
            },
        },
        "/api/vendas/": {
            "get": {
                "tags": ["Vendas"],
                "summary": "Listar pedidos",
                "responses": {"200": {"description": "Lista de pedidos"}},
            },
            "post": {
                "tags": ["Vendas"],
                "summary": "Realizar venda",
                "requestBody": {
                    "required": True,
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/VendaInput"}}},
                },
                "responses": {
                    "201": {"description": "Venda realizada com sucesso"},
                    "400": {"description": "Estoque insuficiente ou dados inválidos"},
                    "403": {"description": "Sem permissão"},
                },
            },
        },
    },
}


def openapi_spec(request):
    return JsonResponse(_OPENAPI_SPEC)


def swagger_ui(request):
    html = """<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <title>Distribuidora API — Docs</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <link rel="stylesheet" href="https://unpkg.com/swagger-ui-dist@5/swagger-ui.css">
</head>
<body>
  <div id="swagger-ui"></div>
  <script src="https://unpkg.com/swagger-ui-dist@5/swagger-ui-bundle.js"></script>
  <script>
    SwaggerUIBundle({
      url: "/api/openapi.json",
      dom_id: "#swagger-ui",
      presets: [SwaggerUIBundle.presets.apis, SwaggerUIBundle.SwaggerUIStandalonePreset],
      layout: "BaseLayout",
      persistAuthorization: true,
    });
  </script>
</body>
</html>"""
    return HttpResponse(html, content_type="text/html")
