from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin

from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(ModelAdmin):
    list_display = ("timestamp", "user", "action", "model_name", "object_repr", "ip_address")
    list_display_links = ("timestamp",)
    list_filter = ("action", "model_name", "timestamp")
    search_fields = ("user__username", "object_repr", "model_name", "ip_address")
    date_hierarchy = "timestamp"
    compressed_fields = True
    show_full_result_count = False
    warn_unsaved_change = True
    readonly_fields = (
        "user", "action", "model_name", "object_id", "object_repr",
        "changes", "ip_address", "user_agent", "timestamp",
    )

    fieldsets = (
        (_("Evento"), {
            "fields": ("user", "action", "timestamp", "ip_address", "user_agent"),
            "classes": ["tab"],
        }),
        (_("Objeto"), {
            "fields": ("model_name", "object_id", "object_repr"),
            "classes": ["tab"],
        }),
        (_("Cambios"), {
            "fields": ("changes",),
            "classes": ["tab"],
        }),
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
