from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin, TabularInline

from apps.audit.mixins import AuditMixin

from .models import CallLog, Contact, EmailLog, Purchase, SocialProfile


class PurchaseInline(TabularInline):
    model = Purchase
    extra = 0
    fields = ["date", "amount", "description"]


class EmailLogInline(TabularInline):
    model = EmailLog
    extra = 0
    fields = ["date", "direction", "subject"]


class CallLogInline(TabularInline):
    model = CallLog
    extra = 0
    fields = ["date", "direction", "duration_minutes", "notes"]


class SocialProfileInline(TabularInline):
    model = SocialProfile
    extra = 0
    fields = ["network", "url"]


STATUS_COLORS = {
    Contact.STATUS_LEAD:     ("bg-blue-100 text-blue-700",    "dark:bg-blue-900/30 dark:text-blue-300"),
    Contact.STATUS_PROSPECT: ("bg-yellow-100 text-yellow-700", "dark:bg-yellow-900/30 dark:text-yellow-300"),
    Contact.STATUS_CLIENT:   ("bg-green-100 text-green-700",   "dark:bg-green-900/30 dark:text-green-300"),
    Contact.STATUS_INACTIVE: ("bg-gray-100 text-gray-600",     "dark:bg-gray-800 dark:text-gray-400"),
}


@admin.register(Contact)
class ContactAdmin(AuditMixin, ModelAdmin):
    list_display   = ["name", "email", "company", "status_badge", "created_at"]
    list_filter    = ["status", "created_at"]
    search_fields  = ["name", "email", "company"]
    date_hierarchy = "created_at"
    warn_unsaved_changes = True

    fieldsets = [
        (
            _("Información general"),
            {
                "fields": ["name", "email", "phone", "company", "status"],
                "classes": ["tab"],
            },
        ),
        (
            _("Historial"),
            {
                "fields": [],
                "classes": ["tab"],
            },
        ),
    ]
    inlines = [PurchaseInline, EmailLogInline, CallLogInline, SocialProfileInline]
    actions = ["mark_inactive"]

    @admin.display(description=_("Estado"))
    def status_badge(self, obj):
        light, dark = STATUS_COLORS.get(obj.status, ("bg-gray-100 text-gray-600", ""))
        label = obj.get_status_display()
        return format_html(
            '<span class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium {} {}">{}</span>',
            light, dark, label,
        )

    @admin.action(description=_("Marcar como inactivos"))
    def mark_inactive(self, request, queryset):
        updated = queryset.update(status=Contact.STATUS_INACTIVE)
        self.message_user(request, _("%(n)d contacto(s) marcados como inactivos.") % {"n": updated})
