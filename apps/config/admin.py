from django.contrib import admin
from django.db.models import Case, IntegerField, Value, When
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin

from .forms import SiteConfigForm
from .models import SiteConfig


_TYPE_COLORS = {
    SiteConfig.ValueType.STR: ("bg-blue-100 text-blue-800", "Texto"),
    SiteConfig.ValueType.INT: ("bg-purple-100 text-purple-800", "Entero"),
    SiteConfig.ValueType.BOOL: ("bg-green-100 text-green-800", "Bool"),
    SiteConfig.ValueType.JSON: ("bg-yellow-100 text-yellow-800", "JSON"),
}


@admin.register(SiteConfig)
class SiteConfigAdmin(ModelAdmin):
    form = SiteConfigForm
    list_display = ("key_display", "value_type_badge", "visibility_badge", "description_short", "value_preview")
    list_display_links = ("key_display",)
    list_filter = ("value_type", "is_public")
    search_fields = ("key", "description")
    ordering = ("key",)
    warn_unsaved_change = True

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        group_cases = [
            When(key__startswith="site_", then=Value(1)),
            When(key__in=["contact_email", "support_email"], then=Value(1)),
            When(key__in=["max_upload_size_mb", "session_timeout_minutes", "items_per_page"], then=Value(2)),
            When(key__startswith="enable_", then=Value(3)),
            When(key__startswith="email_", then=Value(4)),
        ]
        return qs.annotate(
            group_order=Case(*group_cases, default=Value(9), output_field=IntegerField())
        ).order_by("group_order", "key")

    @admin.display(description=_("Clave"))
    def key_display(self, obj):
        return format_html(
            '<code class="font-mono text-sm bg-gray-100 dark:bg-gray-800 px-2 py-0.5 rounded">{}</code>',
            obj.key,
        )

    @admin.display(description=_("Tipo"))
    def value_type_badge(self, obj):
        css, label = _TYPE_COLORS.get(obj.value_type, ("bg-gray-100 text-gray-800", obj.value_type))
        return format_html(
            '<span class="text-xs font-medium px-2 py-0.5 rounded-full {}">{}</span>',
            css,
            label,
        )

    @admin.display(description=_("Visibilidad"), boolean=False)
    def visibility_badge(self, obj):
        if obj.is_public:
            return format_html(
                '<span class="text-xs font-medium px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800">{}</span>',
                _("Pública"),
            )
        return format_html(
            '<span class="text-xs font-medium px-2 py-0.5 rounded-full bg-gray-100 text-gray-500">{}</span>',
            _("Privada"),
        )

    @admin.display(description=_("Descripción"))
    def description_short(self, obj):
        if not obj.description:
            return "—"
        return obj.description

    @admin.display(description=_("Valor"))
    def value_preview(self, obj):
        text = obj.value or ""
        if len(text) > 60:
            text = text[:60] + "…"
        return text

    @admin.display(description=_("tipo de valor"))
    def value_type_display(self, obj):
        css, label = _TYPE_COLORS.get(obj.value_type, ("bg-gray-100 text-gray-800", obj.value_type))
        return format_html(
            '<span class="text-xs font-medium px-2 py-0.5 rounded-full {}">{}</span>',
            css,
            label,
        )

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ("key", "value_type_display")
        return ()

    def get_fieldsets(self, request, obj=None):
        if obj:
            return (
                (None, {"fields": ("key", "value_type_display", "value")}),
                (_("Metadatos"), {"fields": ("description", "is_public")}),
            )
        return (
            (None, {"fields": ("key", "value_type", "value")}),
            (_("Metadatos"), {"fields": ("description", "is_public")}),
        )

    def has_delete_permission(self, request, obj=None):
        return False
