from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "admin", "Administrador"
        PM = "pm", "Project Manager"
        TRANSLATOR = "translator", "Traductor"
        REVIEWER = "reviewer", "Revisor"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.TRANSLATOR,
        verbose_name="rol",
    )
    erp_employee_id = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        verbose_name="ID empleado ERP",
        help_text="Identificador del colaborador en el ERP externo.",
    )

    class Meta:
        verbose_name = "usuario"
        verbose_name_plural = "usuarios"

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
