from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ConfigConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.config"
    verbose_name = _("Configuración")

    plugin_urls = []
    plugin_middleware = []
    plugin_settings = {}

    def ready(self):
        import apps.config.signals  # noqa: F401
