from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _


class AuditLog(models.Model):
    class Action(models.TextChoices):
        CREATE = "create", _("Crear")
        UPDATE = "update", _("Actualizar")
        DELETE = "delete", _("Eliminar")
        LOGIN = "login", _("Inicio de sesión")
        LOGOUT = "logout", _("Cierre de sesión")
        VIEW = "view", _("Ver")

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="audit_logs",
        verbose_name=_("usuario"),
    )
    action = models.CharField(
        max_length=20,
        choices=Action.choices,
        verbose_name=_("acción"),
    )
    model_name = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_("modelo"),
    )
    object_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name=_("ID objeto"),
    )
    object_repr = models.CharField(
        max_length=200,
        verbose_name=_("representación del objeto"),
    )
    changes = models.JSONField(
        null=True,
        blank=True,
        verbose_name=_("cambios"),
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name=_("dirección IP"),
    )
    user_agent = models.CharField(
        max_length=300,
        blank=True,
        null=True,
        verbose_name=_("user agent"),
    )
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("fecha y hora"),
    )

    class Meta:
        verbose_name = _("registro de auditoría")
        verbose_name_plural = _("registros de auditoría")
        ordering = ["-timestamp"]

    def __str__(self):
        return f"{self.action} — {self.model_name} #{self.object_id}"
