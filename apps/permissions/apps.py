from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class PermissionsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.permissions"
    verbose_name = _("Permisos y roles")

    plugin_urls = []
    plugin_middleware = []
    plugin_settings = {}

    def ready(self):
        import apps.permissions.signals  # noqa: F401
