from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ErpSyncConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.erp_sync"
    verbose_name = _("Sincronización ERP")

    plugin_urls = []
    plugin_middleware = []
    plugin_settings = {}
