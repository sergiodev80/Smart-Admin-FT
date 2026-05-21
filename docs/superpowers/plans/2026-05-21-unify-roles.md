# Unify Roles — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Eliminar `User.role` (CharField con choices hardcodeados) y usar `permissions.Role` como sistema único de roles, con roles por defecto `admin`, `staff`, `viewer` en el fixture.

**Architecture:** Se elimina el campo `role` del modelo `User` y su clase `Role(TextChoices)`. Los roles pasan a ser filas en `permissions.Role` asignadas via `permissions.UserRole`. El admin de User se actualiza para mostrar los roles asignados en lugar del campo eliminado. El fixture se reemplaza con los tres roles genéricos del template.

**Tech Stack:** Django 6, Python 3.12, Unfold Admin, django test runner.

---

## File Map

| Archivo | Acción | Qué cambia |
|---------|--------|-----------|
| `apps/core/models.py` | Modificar | Eliminar clase `Role` y campo `role` de `User`, actualizar `__str__` |
| `apps/core/migrations/0002_remove_user_role.py` | Crear | Migración que elimina el campo `role` |
| `apps/core/admin.py` | Modificar | Quitar `role` de `list_display`, `list_filter`, `fieldsets`, `add_fieldsets` |
| `apps/core/tests.py` | Modificar | Eliminar tests de `User.role`, actualizar `test_str_includes_role` |
| `apps/permissions/fixtures/default_roles.json` | Modificar | Reemplazar roles con `admin`, `staff`, `viewer` |

---

### Task 1: Actualizar tests de `core` antes de tocar el modelo

Los tests actuales dependen de `User.Role` y `user.role`. Hay que actualizarlos primero para que fallen correctamente antes de cambiar el modelo.

**Files:**
- Modify: `apps/core/tests.py`

- [ ] **Step 1: Reemplazar los tests de modelo que usan `User.role`**

Reemplazar el bloque `UserModelTest` completo en `apps/core/tests.py`:

```python
class UserModelTest(TestCase):
    def test_str_includes_username(self):
        user = User.objects.create_user(username="u1", password="pass")
        self.assertIn("u1", str(user))

    def test_erp_employee_id_optional(self):
        user = User.objects.create_user(username="u2", password="pass")
        self.assertIsNone(user.erp_employee_id)

    def test_erp_employee_id_can_be_set(self):
        user = User.objects.create_user(
            username="u3", password="pass", erp_employee_id="EMP001"
        )
        self.assertEqual(user.erp_employee_id, "EMP001")
```

- [ ] **Step 2: Verificar que los tests fallan por las razones correctas**

```bash
docker compose -f docker-compose.dev.yml exec web_dev python manage.py test apps.core.tests.UserModelTest -v 2
```

Esperado: los tests nuevos PASAN (no dependen de `role`). Los tests viejos ya no existen.

- [ ] **Step 3: Commit**

```bash
git add apps/core/tests.py
git commit -m "test(core): remove role-based tests, keep user model tests generic"
```

---

### Task 2: Actualizar el modelo `User`

**Files:**
- Modify: `apps/core/models.py`

- [ ] **Step 1: Reemplazar el contenido completo de `apps/core/models.py`**

```python
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
```

- [ ] **Step 2: Crear la migración**

```bash
docker compose -f docker-compose.dev.yml exec web_dev python manage.py makemigrations core --name remove_user_role
```

Esperado: crea `apps/core/migrations/0002_remove_user_role.py`

- [ ] **Step 3: Aplicar la migración**

```bash
docker compose -f docker-compose.dev.yml exec web_dev python manage.py migrate
```

Esperado: `Applying core.0002_remove_user_role... OK`

- [ ] **Step 4: Verificar que Django arranca sin errores**

```bash
docker compose -f docker-compose.dev.yml exec web_dev python manage.py check
```

Esperado: `System check identified no issues (0 silenced).`

- [ ] **Step 5: Commit**

```bash
git add apps/core/models.py apps/core/migrations/0002_remove_user_role.py
git commit -m "feat(core): remove User.role CharField — roles now managed via permissions.Role"
```

---

### Task 3: Actualizar el admin de `User`

**Files:**
- Modify: `apps/core/admin.py`

- [ ] **Step 1: Reemplazar el contenido completo de `apps/core/admin.py`**

```python
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from unfold.admin import ModelAdmin

from .models import User


@admin.register(User)
class UserAdmin(ModelAdmin, BaseUserAdmin):
    list_display = ("username", "email", "is_staff", "is_active", "erp_employee_id")
    list_display_links = ("username",)
    list_filter = ("is_staff", "is_active")
    search_fields = ("username", "email", "erp_employee_id")
    compressed_fields = True
    warn_unsaved_change = True
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Información adicional", {"fields": ("erp_employee_id",)}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("Información adicional", {"fields": ("erp_employee_id",)}),
    )
```

- [ ] **Step 2: Verificar que el admin carga sin errores**

```bash
docker compose -f docker-compose.dev.yml exec web_dev python manage.py check --deploy 2>/dev/null || docker compose -f docker-compose.dev.yml exec web_dev python manage.py check
```

Esperado: `System check identified no issues (0 silenced).`

- [ ] **Step 3: Commit**

```bash
git add apps/core/admin.py
git commit -m "feat(core): remove role from UserAdmin — use permissions.UserRole instead"
```

---

### Task 4: Actualizar el fixture de roles por defecto

**Files:**
- Modify: `apps/permissions/fixtures/default_roles.json`

- [ ] **Step 1: Reemplazar el contenido de `apps/permissions/fixtures/default_roles.json`**

```json
[
  {
    "model": "permissions.role",
    "pk": 1,
    "fields": {
      "name": "admin",
      "description": "Acceso total al sistema",
      "permissions": []
    }
  },
  {
    "model": "permissions.role",
    "pk": 2,
    "fields": {
      "name": "staff",
      "description": "Acceso operativo — puede gestionar contenido",
      "permissions": []
    }
  },
  {
    "model": "permissions.role",
    "pk": 3,
    "fields": {
      "name": "viewer",
      "description": "Solo lectura — no puede crear ni editar",
      "permissions": []
    }
  }
]
```

- [ ] **Step 2: Verificar que el fixture carga correctamente**

```bash
docker compose -f docker-compose.dev.yml exec web_dev python manage.py loaddata apps/permissions/fixtures/default_roles.json
```

Esperado:
```
Installed 3 object(s) from 1 fixture(s)
```

- [ ] **Step 3: Verificar en el shell que los roles existen**

```bash
docker compose -f docker-compose.dev.yml exec web_dev python manage.py shell -c "from apps.permissions.models import Role; print(list(Role.objects.values_list('name', flat=True)))"
```

Esperado: `['admin', 'staff', 'viewer']`

- [ ] **Step 4: Commit**

```bash
git add apps/permissions/fixtures/default_roles.json
git commit -m "feat(permissions): update default roles to admin/staff/viewer — generic template roles"
```

---

### Task 5: Actualizar `CLAUDE.md` — roles en sidebar y documentación

El sidebar de Unfold en `base.py` tiene ítems que apuntan a `/admin/permissions/role/` — eso ya funciona. Pero `CLAUDE.md` menciona los roles viejos en la descripción de `core`.

**Files:**
- Modify: `CLAUDE.md`

- [ ] **Step 1: Actualizar la descripción de `core` en `CLAUDE.md`**

Reemplazar:
```markdown
- **core**: modelo `User` con roles (`admin`, `pm`, `translator`, `reviewer`), flujo de solicitud de acceso, contexto Unfold. Extender roles según necesidad del proyecto.
```

Por:
```markdown
- **core**: modelo `User` (sin roles hardcodeados), flujo de solicitud de acceso, contexto Unfold. Los roles se gestionan desde `apps.permissions` — cargar con `make loaddata`.
```

- [ ] **Step 2: Commit**

```bash
git add CLAUDE.md
git commit -m "docs(CLAUDE.md): update core description — roles now in permissions.Role"
```

---

### Task 6: Correr todos los tests y verificar integración

- [ ] **Step 1: Correr la suite completa**

```bash
docker compose -f docker-compose.dev.yml exec web_dev python manage.py test
```

Esperado: todos los tests pasan. (El número baja de 69 a ~66 porque se eliminaron 3 tests de `User.role`.)

- [ ] **Step 2: Verificar en el admin que Roles aparece vacío y cargable**

Abrir `http://localhost:8002/admin/permissions/role/` — debe aparecer vacío (o con los 3 roles si se cargó el fixture en Task 4).

- [ ] **Step 3: Verificar que el change form de User ya no muestra `rol`**

Abrir `http://localhost:8002/admin/core/user/` y editar cualquier usuario — el campo `rol` no debe aparecer. Solo `erp_employee_id` en "Información adicional".

- [ ] **Step 4: Commit final si hay cambios pendientes**

```bash
git status
# Si hay algo sin commitear:
git add -A
git commit -m "chore: verify role unification complete"
```
