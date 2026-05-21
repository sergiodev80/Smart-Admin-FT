from django.db import models
from django.utils.translation import gettext_lazy as _


class SiteConfig(models.Model):
    class ValueType(models.TextChoices):
        STR = "str", _("Texto")
        INT = "int", _("Entero")
        BOOL = "bool", _("Booleano")
        JSON = "json", _("JSON")

    key = models.SlugField(
        max_length=100,
        unique=True,
        verbose_name=_("clave"),
        help_text=_("Identificador único. Ej: max_upload_size"),
    )
    value = models.TextField(
        verbose_name=_("valor"),
        help_text=_("Siempre almacenado como texto."),
    )
    value_type = models.CharField(
        max_length=10,
        choices=ValueType.choices,
        default=ValueType.STR,
        verbose_name=_("tipo de valor"),
    )
    description = models.TextField(
        blank=True,
        verbose_name=_("descripción"),
        help_text=_("Propósito legible de esta configuración."),
    )
    is_public = models.BooleanField(
        default=False,
        verbose_name=_("pública"),
        help_text=_("Si está marcada, se expone en el contexto de templates."),
    )

    class Meta:
        verbose_name = _("configuración del sitio")
        verbose_name_plural = _("configuraciones del sitio")
        ordering = ["key"]

    def __str__(self):
        return self.key
