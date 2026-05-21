from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin

from .models import Notification, WebhookEndpoint


@admin.register(Notification)
class NotificationAdmin(ModelAdmin):
    list_display = ("title", "recipient", "channel", "sent_at", "read_at", "created_at")
    list_filter = ("channel", "sent_at", "read_at")
    search_fields = ("title", "recipient__username", "recipient__email")
    readonly_fields = ("recipient", "title", "body", "channel", "sent_at", "read_at", "payload", "created_at")
    date_hierarchy = "created_at"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return obj is None


@admin.register(WebhookEndpoint)
class WebhookEndpointAdmin(ModelAdmin):
    list_display = ("url", "user", "is_active")
    list_filter = ("is_active",)
    search_fields = ("url", "user__username")
