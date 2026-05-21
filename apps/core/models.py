from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
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
        return self.username
