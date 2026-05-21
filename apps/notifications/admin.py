from django.contrib import admin
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin
from unfold.decorators import display, action

from .models import Notification, WebhookEndpoint


@admin.register(Notification)
class NotificationAdmin(ModelAdmin):
    list_display = ("title", "recipient", "channel", "sent_at", "read_at", "created_at")
    list_display_links = ("title",)
    list_filter = ("channel", "sent_at", "read_at")
    search_fields = ("title", "recipient__username", "recipient__email")
    readonly_fields = ("recipient", "title", "body", "channel", "sent_at", "read_at", "payload", "created_at")
    date_hierarchy = "created_at"
    warn_unsaved_change = True
    actions = ["mark_as_read"]

    fieldsets = (
        (_("Mensaje"), {
            "fields": ("recipient", "title", "body", "channel"),
            "classes": ["tab"],
        }),
        (_("Estado"), {
            "fields": ("sent_at", "read_at", "created_at"),
            "classes": ["tab"],
        }),
        (_("Payload"), {
            "fields": ("payload",),
            "classes": ["tab"],
        }),
    )

    @action(description=_("Marcar seleccionadas como leídas"))
    def mark_as_read(self, request, queryset):
        updated = queryset.filter(read_at__isnull=True).update(read_at=timezone.now())
        self.message_user(request, _(f"{updated} notificaciones marcadas como leídas."))

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return obj is None


@admin.register(WebhookEndpoint)
class WebhookEndpointAdmin(ModelAdmin):
    list_display = ("show_url", "user", "show_signed", "show_active")
    list_display_links = ("show_url",)
    list_filter = ("is_active",)
    search_fields = ("url", "user__username")
    compressed_fields = True
    warn_unsaved_change = True
    change_form_after_template = "notifications/webhook_endpoint_guide.html"

    fieldsets = (
        (
            _("Endpoint"),
            {
                "fields": ("user", "url", "is_active"),
                "description": _(
                    "El sistema enviará un HTTP POST a esta URL cada vez que se dispare "
                    "una notificación con <code>channel='webhook'</code> para el usuario seleccionado."
                ),
            },
        ),
        (
            _("Seguridad"),
            {
                "fields": ("secret",),
                "description": _(
                    "Si se configura un secreto, cada POST incluirá el header "
                    "<code>X-Signature: sha256=&lt;hmac&gt;</code> firmado con HMAC-SHA256. "
                    "Ver la guía de integración abajo para verificarlo en tu receptor."
                ),
            },
        ),
    )

    @display(description=_("URL"), ordering="url")
    def show_url(self, obj):
        from urllib.parse import urlparse
        parsed = urlparse(obj.url)
        domain = parsed.netloc or obj.url
        short = domain[:50] + "…" if len(domain) > 50 else domain
        return f'{short}<br><span style="font-size:11px;color:#9ca3af">{obj.url}</span>'

    show_url.allow_tags = True

    @display(
        description=_("Firmado"),
        label={"signed": "success", "unsigned": "warning"},
    )
    def show_signed(self, obj):
        return "signed" if obj.secret else "unsigned"

    @display(
        description=_("Activo"),
        boolean=True,
        ordering="is_active",
    )
    def show_active(self, obj):
        return obj.is_active
