import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

#integrate key
SECRET_SHHH =  os.environ.get("DJANGO_SECRET_KEY", "dev-only-insecure-key")

DEBUG = False

ALLOWED_HOSTS = ["localhost", "127.0.0.1"]

RENDER_HOSTNAME = os.environ.get("RENDER_EXTERNAL_KEY")

if RENDER_HOSTNAME is not None:
    ALLOWED_HOSTS.append(RENDER_HOSTNAME)

INSTALLED_APPS = [
    "django.contrib.staticfiles",
    "table"
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.common.CommonMiddleware",
]

ROOT_URLCONF = "alan_web.urls"

TMEPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {"context_processors": []},
    }
]

WSGI_APPLICATION = "alan_web.wsgi.application"

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage"
    }
}

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"