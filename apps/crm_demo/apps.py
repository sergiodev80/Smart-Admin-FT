from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class CrmDemoConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.crm_demo"
    verbose_name = _("CRM Demo")

    plugin_urls = [
        {"prefix": "admin/crm-demo/", "urlconf": "apps.crm_demo.urls"},
    ]
    plugin_middleware = []
    plugin_settings = {}
