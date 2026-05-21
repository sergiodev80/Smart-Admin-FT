from django.conf import settings
from django.contrib.auth.models import Permission
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import gettext_lazy as _


class Role(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_("nombre"),
    )
    description = models.TextField(
        blank=True,
        verbose_name=_("descripción"),
    )
    permissions = models.ManyToManyField(
        Permission,
        blank=True,
        verbose_name=_("permisos"),
    )

    class Meta:
        verbose_name = _("rol")
        verbose_name_plural = _("roles")
        ordering = ["name"]

    def __str__(self):
        return self.name


class UserRole(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="user_roles",
        verbose_name=_("usuario"),
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name="user_roles",
        verbose_name=_("rol"),
    )
    assigned_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("asignado el"),
    )
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="roles_assigned",
        verbose_name=_("asignado por"),
    )

    class Meta:
        verbose_name = _("rol de usuario")
        verbose_name_plural = _("roles de usuario")
        unique_together = [("user", "role")]

    def __str__(self):
        return f"{self.user} — {self.role}"


class ObjectPermission(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="object_permissions",
        verbose_name=_("usuario"),
    )
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        verbose_name=_("tipo de contenido"),
    )
    object_id = models.CharField(
        max_length=100,
        verbose_name=_("ID del objeto"),
    )
    permission = models.ForeignKey(
        Permission,
        on_delete=models.CASCADE,
        verbose_name=_("permiso"),
    )

    class Meta:
        verbose_name = _("permiso por objeto")
        verbose_name_plural = _("permisos por objeto")
        unique_together = [("user", "content_type", "object_id", "permission")]

    def __str__(self):
        return f"{self.user} | {self.content_type} #{self.object_id} | {self.permission.codename}"
