"""
Roteamento de URLs — distribuidora
"""
from django.urls import path
from apps import views

urlpatterns = [
    # — Docs —
    path("api/docs/",        views.swagger_ui,   name="swagger-ui"),
    path("api/openapi.json", views.openapi_spec, name="openapi-spec"),

    # — Auth —
    path("api/auth/login/",  views.login,  name="login"),
    path("api/auth/perfil/", views.perfil, name="perfil"),

    # — Usuários —
    path("api/usuarios/",             views.usuarios,        name="usuarios"),
    path("api/usuarios/<str:usuario_id>/", views.usuario_detalhe, name="usuario-detalhe"),

    # — Categorias —
    path("api/categorias/",                    views.categorias,       name="categorias"),
    path("api/categorias/<str:categoria_id>/", views.categoria_detalhe, name="categoria-detalhe"),

    # — Bebidas —
    path("api/bebidas/",                 views.bebidas,       name="bebidas"),
    path("api/bebidas/<str:bebida_id>/", views.bebida_detalhe, name="bebida-detalhe"),

    # — Estoque —
    path("api/estoque/",                          views.estoque,              name="estoque"),
    path("api/estoque/lotes/",                    views.estoque_lotes,        name="estoque-lotes"),
    path("api/estoque/lotes/<str:lote_id>/",      views.estoque_lote_detalhe, name="estoque-lote-detalhe"),

    # — Cupons —
    path("api/cupons/",                 views.cupons,       name="cupons"),
    path("api/cupons/<str:cupom_id>/",  views.cupom_detalhe, name="cupom-detalhe"),

    # — Vendas —
    path("api/vendas/", views.vendas, name="vendas"),
]
