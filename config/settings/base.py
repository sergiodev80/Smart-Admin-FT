"""
Base settings — Smart AdminAI Template.
Reemplazar los valores TODO antes de usar en producción.
"""
from pathlib import Path
from dotenv import load_dotenv
from django.utils.translation import gettext_lazy as _
import os

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent.parent

SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")

DEBUG = os.getenv("DEBUG", "False").lower() == "true"

ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "localhost").split(",")

DJANGO_APPS = [
    "unfold",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_htmx",
]

LOCAL_APPS = [
    "apps.core",
    # --- v2 optional apps — uncomment to activate ---
    "apps.notifications",
    "apps.audit",
    "apps.config",
    "apps.permissions",
]

INSTALLED_APPS = DJANGO_APPS + LOCAL_APPS

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "apps.core.middleware.CookieLanguageMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "apps.core.context_processors.unfold_auth_context",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": os.getenv("DB_NAME", "app_db"),
        "USER": os.getenv("DB_USER", "django_user"),
        "PASSWORD": os.getenv("DB_PASSWORD", "django_pass"),
        "HOST": os.getenv("DB_HOST", "localhost"),
        "PORT": os.getenv("DB_PORT", "5432"),
    },
}

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# Email
EMAIL_BACKEND = os.getenv("EMAIL_BACKEND", "django.core.mail.backends.console.EmailBackend")
EMAIL_HOST = os.getenv("EMAIL_HOST", "")
EMAIL_PORT = int(os.getenv("EMAIL_PORT", "587"))
EMAIL_HOST_USER = os.getenv("EMAIL_HOST_USER", "")
EMAIL_HOST_PASSWORD = os.getenv("EMAIL_HOST_PASSWORD", "")
EMAIL_USE_TLS = os.getenv("EMAIL_USE_TLS", "False").lower() == "true"
EMAIL_USE_SSL = os.getenv("EMAIL_USE_SSL", "False").lower() == "true"
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "noreply@example.com")

# Internationalization
LANGUAGE_CODE = "es"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True
LANGUAGE_COOKIE_NAME = "django_language"
LANGUAGE_COOKIE_AGE = 365 * 24 * 60 * 60

LANGUAGES = [
    ("es", "Español"),
    ("en", "English"),
]

LOCALE_PATHS = [
    BASE_DIR / "locale",
]

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {"class": "logging.StreamHandler"},
    },
    "loggers": {
        "apps": {"handlers": ["console"], "level": "DEBUG", "propagate": False},
    },
}

STATIC_URL = "static/"
STATIC_ROOT = Path(os.getenv("STATIC_ROOT", str(BASE_DIR / "static")))

MEDIA_URL = "/media/"
MEDIA_ROOT = Path(os.getenv("MEDIA_ROOT", str(BASE_DIR / "media")))

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

AUTH_USER_MODEL = "core.User"

LOGIN_URL = "/admin/login/"
LOGIN_REDIRECT_URL = "/admin/"

AUTHENTICATION_BACKENDS = [
    "apps.core.backends.EmailOrUsernameBackend",
]

# Unfold Admin Config — personalizar por proyecto
UNFOLD = {
    "SITE_TITLE": "TODO: Nombre del proyecto",
    "SITE_HEADER": "TODO: Nombre del proyecto",
    "SITE_SYMBOL": "admin_panel_settings",
    "SHOW_HISTORY": True,
    "SHOW_VIEW_ON_SITE": True,
    "SHOW_LANGUAGES": True,
    "DASHBOARD_CALLBACK": "apps.core.dashboard.dashboard_callback",
    "COLORS": {
        "primary": {
            "50": "239 246 255",
            "100": "219 234 254",
            "200": "191 219 254",
            "300": "147 197 253",
            "400": "96 165 250",
            "500": "59 130 246",
            "600": "37 99 235",
            "700": "29 78 216",
            "800": "30 64 175",
            "900": "30 58 138",
            "950": "23 37 84",
        },
    },
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": False,
        "navigation": [
            {
                "title": _("Administración"),
                "separator": False,
                "collapsible": True,
                "items": [
                    {
                        "title": _("Usuarios"),
                        "icon": "group",
                        "link": "/admin/core/user/",
                    },
                    {
                        "title": _("Roles"),
                        "icon": "shield_person",
                        "link": "/admin/permissions/role/",
                    },
                    {
                        "title": _("Roles de usuario"),
                        "icon": "manage_accounts",
                        "link": "/admin/permissions/userrole/",
                    },
                    {
                        "title": _("Permisos por objeto"),
                        "icon": "lock",
                        "link": "/admin/permissions/objectpermission/",
                    },
                    {
                        "title": _("Notificaciones"),
                        "icon": "notifications",
                        "link": "/admin/notifications/notification/",
                    },
                    {
                        "title": _("Endpoints webhook"),
                        "icon": "webhook",
                        "link": "/admin/notifications/webhookendpoint/",
                    },
                    {
                        "title": _("Configuraciones del sitio"),
                        "icon": "settings",
                        "link": "/admin/config/siteconfig/",
                    },
                    {
                        "title": _("Registros de auditoría"),
                        "icon": "history",
                        "link": "/admin/audit/auditlog/",
                    },
                ],
            },
            # --- Agregar secciones del proyecto aquí ---
        ],
    },
}

# --- Plugin auto-registration ---
# Must run after INSTALLED_APPS and MIDDLEWARE are fully defined.
from config.plugins import autoregister_plugins  # noqa: E402

_plugin_urls = autoregister_plugins(INSTALLED_APPS, MIDDLEWARE, globals())
