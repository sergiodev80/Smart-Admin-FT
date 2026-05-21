from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class Notification(models.Model):
    class Channel(models.TextChoices):
        IN_APP = "in_app", _("En la app")
        EMAIL = "email", _("Email")
        WEBHOOK = "webhook", _("Webhook")

    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name=_("destinatario"),
    )
    title = models.CharField(max_length=200, verbose_name=_("título"))
    body = models.TextField(verbose_name=_("cuerpo"))
    channel = models.CharField(
        max_length=20,
        choices=Channel.choices,
        verbose_name=_("canal"),
    )
    read_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("leída el"),
    )
    sent_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("enviada el"),
    )
    payload = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_("payload"),
        help_text=_("Datos adicionales para webhooks."),
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("creada el"))

    class Meta:
        verbose_name = _("notificación")
        verbose_name_plural = _("notificaciones")
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} → {self.recipient}"


class WebhookEndpoint(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="webhook_endpoints",
        verbose_name=_("usuario"),
    )
    url = models.URLField(verbose_name=_("URL"))
    is_active = models.BooleanField(default=True, verbose_name=_("activo"))
    secret = models.CharField(
        max_length=200,
        blank=True,
        verbose_name=_("secreto"),
        help_text=_("Usado para firmar el payload con HMAC-SHA256."),
    )

    class Meta:
        verbose_name = _("endpoint webhook")
        verbose_name_plural = _("endpoints webhook")

    def __str__(self):
        return self.url
