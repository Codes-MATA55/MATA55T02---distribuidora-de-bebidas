"""
Django settings — Distribuidora de Bebidas
"""
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = os.environ.get("DJANGO_SECRET_KEY", "django-insecure-distribuidora-poo-2026")

DEBUG = os.environ.get("DJANGO_DEBUG", "True") == "True"

ALLOWED_HOSTS = os.environ.get("ALLOWED_HOSTS", "*").split(",")

INSTALLED_APPS = [
    "django.contrib.contenttypes",
    "django.contrib.staticfiles",
    "apps",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "distribuidora.urls"

WSGI_APPLICATION = "distribuidora.wsgi.application"

DATABASES = {}   # Não usa banco — persistência via JSON

LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Bahia"
USE_I18N = True
USE_TZ = True

STATIC_URL = "/static/"

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Caminho do JSON mockado
DB_JSON_PATH = os.environ.get(
    "DB_JSON_PATH",
    str(BASE_DIR / "data" / "db.json"),
)
