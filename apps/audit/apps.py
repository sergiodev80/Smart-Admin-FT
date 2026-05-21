from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AuditConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.audit"
    verbose_name = _("Auditoría")

    plugin_urls = []
    plugin_middleware = [
        {
            "middleware": "apps.audit.middleware.AuditMiddleware",
            "insert_after": "django.contrib.auth.middleware.AuthenticationMiddleware",
        }
    ]
    plugin_settings = {}

    def ready(self):
        import apps.audit.signals  # noqa: F401
