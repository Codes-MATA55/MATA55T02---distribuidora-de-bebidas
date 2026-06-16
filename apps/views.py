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

# DICA: Se der ModuleNotFoundError aqui, altere para: from .servicos import ...
from apps.servicos import (
    ServicoAutenticacao,
    ServicoBebida,
    ServicoCategoria,
    ServicoEstoque,
    ServicoUsuario,
    ServicoPedido,
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
    return _erro("Método não permitido.", status=405)


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
    return _erro("Método não permitido.", status=405)


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
    return _erro("Método não permitido.", status=405)


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
# PEDIDOS / REQUISIÇÕES INTERNAS
# ─────────────────────────────────────────────────────────────

@csrf_exempt
@requer_autenticacao
def pedidos(request):
    """
    GET  /api/pedidos/  — Lista as requisições de estoque baseando-se no papel
    POST /api/pedidos/  — Cria uma nova requisição e processa a baixa física FEFO
    """
    svc = ServicoPedido()
    try:
        if request.method == "GET":
            return _sucesso(svc.listar(request.usuario))
        
        if request.method == "POST":
            dados = _body(request)
            return _sucesso(svc.criar_requisicao(request.usuario, dados), status=201)
            
    except PermissionError as e:
        return _erro(str(e), status=403)
    except ValueError as e:
        return _erro(str(e))
        
    return _erro("Método não permitido.", status=405)

# ─────────────────────────────────────────────────────────────
# PEDIDOS / REQUISIÇÕES INTERNAS
# ─────────────────────────────────────────────────────────────

@csrf_exempt
@requer_autenticacao
def pedido_cancelar(request, pedido_id):
    """
    POST /api/pedidos/<id>/cancelar/ — Cancela uma requisição em rascunho ou pendente
    """
    svc = ServicoPedido()
    try:
        if request.method == "POST":
            return _sucesso(svc.cancelar_requisicao(request.usuario, pedido_id))
            
    except PermissionError as e:
        return _erro(str(e), status=403)
    except ValueError as e:
        return _erro(str(e))
        
    return _erro("Método não permitido.", status=405)


@csrf_exempt
@requer_autenticacao
def pedido_aprovar(request, pedido_id):
    """
    POST /api/pedidos/<id>/aprovar/ — Aprova uma requisição pendente:
    executa a baixa física (FEFO) e libera a reserva de estoque.
    """
    svc = ServicoPedido()
    try:
        if request.method == "POST":
            return _sucesso(svc.aprovar_requisicao(request.usuario, pedido_id))

    except PermissionError as e:
        return _erro(str(e), status=403)
    except ValueError as e:
        return _erro(str(e))

    return _erro("Método não permitido.", status=405)


@csrf_exempt
@requer_autenticacao
def pedido_expedir(request, pedido_id):
    """
    POST /api/pedidos/<id>/expedir/ — Registra a saída física das
    mercadorias do depósito (expedição/despacho). Requer status CONCLUIDO.
    """
    svc = ServicoPedido()
    try:
        if request.method == "POST":
            return _sucesso(svc.expedir_requisicao(request.usuario, pedido_id))

    except PermissionError as e:
        return _erro(str(e), status=403)
    except ValueError as e:
        return _erro(str(e))

    return _erro("Método não permitido.", status=405)

# ─────────────────────────────────────────────────────────────
# SWAGGER / OPENAPI
# ─────────────────────────────────────────────────────────────

_OPENAPI_SPEC = {
    "openapi": "3.0.3",
    "info": {
        "title": "Distribuidora de Bebidas",
        "version": "1.0.0",
        "description": "API REST para gerenciamento logístico de bebidas em alta escala",
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
                    "tipo": {"type": "string", "enum": ["administrador", "gerencia", "requisitante", "estoque"]},
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
                "required": ["nome", "categoria_id", "marca", "volume_ml", "fornecedor"],
                "properties": {
                    "nome": {"type": "string", "example": "Heineken 600ml"},
                    "categoria_id": {"type": "string", "example": "cat-abc123"},
                    "marca": {"type": "string", "example": "Heineken"},
                    "volume_ml": {"type": "integer", "example": 600},
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
                    "data_fabricacao": {"type": "string", "format": "date", "example": "2026-01-01"},
                    "data_validade": {"type": "string", "format": "date", "example": "2027-01-01"},
                    "codigo_lote": {"type": "string", "example": "LOT-2026-001"},
                },
            },
            "PedidoInput": {
                "type": "object",
                "required": ["motivo", "itens"],
                "properties": {
                    "motivo": {"type": "string", "enum": ["abastecimento_interno", "transferencia_filial", "avaria_perda", "remanejo"], "example": "abastecimento_interno"},
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
                "security": [],
                "requestBody": {"required": True, "content": {"application/json": {"schema": {"$ref": "#/components/schemas/LoginInput"}}}},
                "responses": {"200": {"description": "Token JWT gerado"}, "401": {"description": "Credenciais inválidas"}},
            }
        },
        "/api/auth/perfil/": {
            "get": {
                "tags": ["Auth"],
                "summary": "Perfil do usuário logado",
                "responses": {"200": {"description": "Dados do usuário"}, "401": {"description": "Não autenticado"}},
            }
        },
        "/api/usuarios/": {
            "get": {"tags": ["Usuários"], "summary": "Listar usuários", "responses": {"200": {"description": "Lista de usuários"}}},
            "post": {
                "tags": ["Usuários"],
                "summary": "Criar usuário",
                "requestBody": {"required": True, "content": {"application/json": {"schema": {"$ref": "#/components/schemas/UsuarioInput"}}}},
                "responses": {"201": {"description": "Usuário criado"}},
            },
        },
        "/api/categorias/": {
            "get": {"tags": ["Categorias"], "summary": "Listar categorias", "responses": {"200": {"description": "Lista de categorias"}}},
            "post": {
                "tags": ["Categorias"],
                "summary": "Criar categoria",
                "requestBody": {"required": True, "content": {"application/json": {"schema": {"$ref": "#/components/schemas/CategoriaInput"}}}},
                "responses": {"201": {"description": "Categoria criada"}},
            },
        },
        "/api/bebidas/": {
            "get": {"tags": ["Bebidas"], "summary": "Listar bebidas", "responses": {"200": {"description": "Lista de bebidas"}}},
            "post": {
                "tags": ["Bebidas"],
                "summary": "Criar bebida",
                "requestBody": {"required": True, "content": {"application/json": {"schema": {"$ref": "#/components/schemas/BebidaInput"}}}},
                "responses": {"201": {"description": "Bebida criada"}},
            },
        },
        "/api/estoque/": {
            "get": {"tags": ["Estoque"], "summary": "Listar estoque consolidado", "responses": {"200": {"description": "Estoque de bebidas"}}}
        },
        "/api/estoque/lotes/": {
            "post": {
                "tags": ["Estoque"],
                "summary": "Adicionar lote físico",
                "requestBody": {"required": True, "content": {"application/json": {"schema": {"$ref": "#/components/schemas/LoteInput"}}}},
                "responses": {"201": {"description": "Lote registrado"}},
            }
        },
        "/api/pedidos/": {
            "get": {
                "tags": ["Pedidos"],
                "summary": "Listar requisições de estoque",
                "responses": {"200": {"description": "Lista de movimentações internas"}}
            },
            "post": {
                "tags": ["Pedidos"],
                "summary": "Criar requisição de material (reserva o estoque)",
                "requestBody": {
                    "required": True,
                    "content": {"application/json": {"schema": {"$ref": "#/components/schemas/PedidoInput"}}}
                },
                "responses": {
                    "201": {"description": "Requisição criada e estoque reservado (status: pendente)"},
                    "400": {"description": "Estoque insuficiente para reserva"}
                }
            }
        },
        "/api/pedidos/{pedido_id}/cancelar/": {
            "post": {
                "tags": ["Pedidos"],
                "summary": "Cancelar requisição",
                "parameters": [{"name": "pedido_id", "in": "path", "required": True, "schema": {"type": "string"}}],
                "responses": {
                    "200": {"description": "Requisição cancelada (libera a reserva, se houver)"},
                    "400": {"description": "Regras de negócio impedem cancelamento"}
                }
            }
        },
        "/api/pedidos/{pedido_id}/aprovar/": {
            "post": {
                "tags": ["Pedidos"],
                "summary": "Aprovar requisição pendente",
                "description": "Executa a baixa física dos lotes (FEFO) e libera a reserva correspondente. Transiciona a requisição de 'pendente' para 'concluido'.",
                "parameters": [{"name": "pedido_id", "in": "path", "required": True, "schema": {"type": "string"}}],
                "responses": {
                    "200": {"description": "Requisição aprovada e estoque baixado"},
                    "400": {"description": "Pedido não está pendente, ou estoque insuficiente para baixa"}
                }
            }
        },
        "/api/pedidos/{pedido_id}/expedir/": {
            "post": {
                "tags": ["Pedidos"],
                "summary": "Expedir requisição concluída",
                "description": "Registra a saída física das mercadorias do depósito. Só pode ocorrer após aprovação (status 'concluido'). Não altera o estoque — a baixa já foi feita na aprovação.",
                "parameters": [{"name": "pedido_id", "in": "path", "required": True, "schema": {"type": "string"}}],
                "responses": {
                    "200": {"description": "Expedição registrada, pedido agora com status 'expedido'"},
                    "400": {"description": "Pedido não está concluído"},
                    "403": {"description": "Sem permissão para expedir"}
                }
            }
        }
    }
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