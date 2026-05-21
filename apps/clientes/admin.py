from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin
from unfold.decorators import display, action

from apps.audit.mixins import AuditMixin
from apps.clientes.models import Cliente


@admin.register(Cliente)
class ClienteAdmin(AuditMixin, ModelAdmin):
    list_display = ("nombre", "email", "telefono", "estado_badge", "created_at")
    list_filter = ("estado",)
    search_fields = ("nombre", "email")
    readonly_fields = ("created_at",)
    compressed_fields = True
    warn_unsaved_change = True

    fieldsets = (
        (
            _("Información"),
            {
                "classes": ["tab"],
                "fields": ("nombre", "email", "telefono"),
            },
        ),
        (
            _("Estado"),
            {
                "classes": ["tab"],
                "fields": ("estado", "created_at"),
            },
        ),
    )

    actions = ["marcar_inactivo"]

    @display(
        description=_("Estado"),
        label={
            Cliente.Estado.ACTIVO: "success",
            Cliente.Estado.INACTIVO: "danger",
        },
    )
    def estado_badge(self, obj):
        return obj.estado

    @action(description=_("Marcar como inactivo"))
    def marcar_inactivo(self, request, queryset):
        queryset.update(estado=Cliente.Estado.INACTIVO)
