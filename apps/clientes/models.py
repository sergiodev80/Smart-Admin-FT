from django.db import models
from django.utils.translation import gettext_lazy as _


class Cliente(models.Model):
    class Estado(models.TextChoices):
        ACTIVO = "activo", _("Activo")
        INACTIVO = "inactivo", _("Inactivo")

    nombre = models.CharField(max_length=200, verbose_name=_("nombre"))
    email = models.EmailField(unique=True, verbose_name=_("email"))
    telefono = models.CharField(
        max_length=30,
        blank=True,
        verbose_name=_("teléfono"),
    )
    estado = models.CharField(
        max_length=10,
        choices=Estado.choices,
        default=Estado.ACTIVO,
        verbose_name=_("estado"),
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_("creado el"))

    class Meta:
        verbose_name = _("cliente")
        verbose_name_plural = _("clientes")
        ordering = ["-created_at"]

    def __str__(self):
        return self.nombre
