from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin

from .forms import SiteConfigForm
from .models import SiteConfig


@admin.register(SiteConfig)
class SiteConfigAdmin(ModelAdmin):
    form = SiteConfigForm
    list_display = ("key", "is_public", "description", "value")
    list_filter = ("value_type", "is_public")
    search_fields = ("key", "description")

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ("key", "value_type")
        return ()

    def get_fieldsets(self, request, obj=None):
        if obj:
            return (
                (None, {"fields": ("key", "value_type", "value")}),
                (_("Metadatos"), {"fields": ("description", "is_public")}),
            )
        return (
            (None, {"fields": ("key", "value_type", "value")}),
            (_("Metadatos"), {"fields": ("description", "is_public")}),
        )

    def has_delete_permission(self, request, obj=None):
        return False
