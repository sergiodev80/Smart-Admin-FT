from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin

from .models import SiteConfig


@admin.register(SiteConfig)
class SiteConfigAdmin(ModelAdmin):
    list_display = ("key", "is_public", "description", "value")
    list_filter = ("value_type", "is_public")
    search_fields = ("key", "description")
    readonly_fields = ("key", "value_type", "cast_preview")
    fieldsets = (
        (None, {"fields": ("key", "value_type", "value", "cast_preview")}),
        (_("Metadatos"), {"fields": ("description", "is_public")}),
    )

    def has_delete_permission(self, request, obj=None):
        return False

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return self.readonly_fields
        return ("cast_preview",)

    @admin.display(description=_("valor interpretado"))
    def cast_preview(self, obj):
        from .services import ConfigService
        return repr(ConfigService._cast(obj.value, obj.value_type))
