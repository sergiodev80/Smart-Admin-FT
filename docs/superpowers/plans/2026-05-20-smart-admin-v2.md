# Smart Admin FT v2 — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add four independent plug-and-play Django apps (notifications, audit, config, permissions) to the Smart Admin FT template, each activatable by toggling `LOCAL_APPS`.

**Architecture:** Each app lives in `apps/<name>/` and follows the same internal structure (models, admin, services, signals, tests, README). Apps have no hard dependencies between them — communication happens via Django signals. All ModelAdmin classes inherit from `unfold.admin.ModelAdmin`. All UI strings use `_()` / `{% trans %}`.

**Tech Stack:** Django 6, Python 3.12, Unfold Admin, PostgreSQL, Docker, Django i18n (gettext)

---

## File Map

### New files created across all tasks

```
apps/config/__init__.py
apps/config/apps.py
apps/config/models.py
apps/config/admin.py
apps/config/services.py
apps/config/signals.py
apps/config/tests.py
apps/config/migrations/__init__.py
apps/config/migrations/0001_initial.py
apps/config/README.md

apps/audit/__init__.py
apps/audit/apps.py
apps/audit/models.py
apps/audit/admin.py
apps/audit/mixins.py
apps/audit/middleware.py
apps/audit/signals.py
apps/audit/tests.py
apps/audit/migrations/__init__.py
apps/audit/migrations/0001_initial.py
apps/audit/README.md

apps/notifications/__init__.py
apps/notifications/apps.py
apps/notifications/models.py
apps/notifications/admin.py
apps/notifications/services.py
apps/notifications/signals.py
apps/notifications/tests.py
apps/notifications/migrations/__init__.py
apps/notifications/migrations/0001_initial.py
apps/notifications/README.md

apps/permissions/__init__.py
apps/permissions/apps.py
apps/permissions/models.py
apps/permissions/admin.py
apps/permissions/signals.py
apps/permissions/tests.py
apps/permissions/migrations/__init__.py
apps/permissions/migrations/0001_initial.py
apps/permissions/migrations/0002_default_roles.py
apps/permissions/fixtures/default_roles.json
apps/permissions/README.md

locale/es/LC_MESSAGES/django.po   (updated each task)
locale/en/LC_MESSAGES/django.po   (updated each task)
```

### Modified files

```
config/settings/base.py           — add commented LOCAL_APPS entries
CLAUDE.md                         — add v2 section
```

---

## Task 1: `apps/config` — Models, Service, Admin, Tests

**Files:**
- Create: `apps/config/__init__.py`
- Create: `apps/config/apps.py`
- Create: `apps/config/models.py`
- Create: `apps/config/services.py`
- Create: `apps/config/signals.py`
- Create: `apps/config/admin.py`
- Create: `apps/config/tests.py`
- Create: `apps/config/migrations/__init__.py`
- Create: `apps/config/README.md`
- Modify: `config/settings/base.py`

- [ ] **Step 1: Write the failing tests**

Create `apps/config/tests.py`:

```python
from django.test import TestCase
from unittest.mock import patch


class SiteConfigModelTest(TestCase):
    def test_create_str_config(self):
        from apps.config.models import SiteConfig
        cfg = SiteConfig.objects.create(
            key="site_name",
            value="Acme Corp",
            value_type="str",
            description="Nombre del sitio",
        )
        self.assertEqual(str(cfg), "site_name")

    def test_create_int_config(self):
        from apps.config.models import SiteConfig
        cfg = SiteConfig.objects.create(key="max_items", value="50", value_type="int")
        self.assertEqual(str(cfg), "max_items")

    def test_key_is_unique(self):
        from apps.config.models import SiteConfig
        from django.db import IntegrityError
        SiteConfig.objects.create(key="dup_key", value="1", value_type="str")
        with self.assertRaises(IntegrityError):
            SiteConfig.objects.create(key="dup_key", value="2", value_type="str")


class ConfigServiceTest(TestCase):
    def setUp(self):
        from apps.config.models import SiteConfig
        SiteConfig.objects.create(key="greeting", value="Hello", value_type="str")
        SiteConfig.objects.create(key="max_size", value="100", value_type="int")
        SiteConfig.objects.create(key="feature_on", value="true", value_type="bool")
        SiteConfig.objects.create(key="meta", value='{"a": 1}', value_type="json")

    def test_get_str(self):
        from apps.config.services import ConfigService
        self.assertEqual(ConfigService.get("greeting"), "Hello")

    def test_get_int(self):
        from apps.config.services import ConfigService
        self.assertEqual(ConfigService.get("max_size"), 100)

    def test_get_bool_true(self):
        from apps.config.services import ConfigService
        self.assertTrue(ConfigService.get("feature_on"))

    def test_get_json(self):
        from apps.config.services import ConfigService
        self.assertEqual(ConfigService.get("meta"), {"a": 1})

    def test_get_missing_returns_default(self):
        from apps.config.services import ConfigService
        self.assertIsNone(ConfigService.get("nonexistent"))
        self.assertEqual(ConfigService.get("nonexistent", default="fallback"), "fallback")

    def test_set_updates_value(self):
        from apps.config.services import ConfigService
        ConfigService.set("greeting", "Hola")
        self.assertEqual(ConfigService.get("greeting"), "Hola")

    def test_cache_is_invalidated_on_save(self):
        from apps.config.services import ConfigService
        from apps.config.models import SiteConfig
        ConfigService.get("greeting")  # populate cache
        cfg = SiteConfig.objects.get(key="greeting")
        cfg.value = "Hi"
        cfg.save()
        self.assertEqual(ConfigService.get("greeting"), "Hi")


class ConfigAdminRegisteredTest(TestCase):
    def test_siteconfig_registered(self):
        from django.contrib import admin
        from apps.config.models import SiteConfig
        self.assertIn(SiteConfig, admin.site._registry)
```

- [ ] **Step 2: Run tests — expect failure**

```bash
make test
```

Expected: `ModuleNotFoundError: No module named 'apps.config'`

- [ ] **Step 3: Create app scaffold**

Create `apps/config/__init__.py` (empty).

Create `apps/config/apps.py`:

```python
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class ConfigConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.config"
    verbose_name = _("Configuración")

    def ready(self):
        import apps.config.signals  # noqa: F401
```

Create `apps/config/migrations/__init__.py` (empty).

- [ ] **Step 4: Create the model**

Create `apps/config/models.py`:

```python
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
```

- [ ] **Step 5: Create the service**

Create `apps/config/services.py`:

```python
import json
import logging

from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)

_cache: dict = {}


class ConfigService:
    @staticmethod
    def get(key: str, default=None):
        if key in _cache:
            return _cache[key]
        try:
            from apps.config.models import SiteConfig
            cfg = SiteConfig.objects.get(key=key)
            value = ConfigService._cast(cfg.value, cfg.value_type)
            _cache[key] = value
            return value
        except Exception:
            return default

    @staticmethod
    def set(key: str, value) -> None:
        from apps.config.models import SiteConfig
        cfg = SiteConfig.objects.get(key=key)
        cfg.value = str(value)
        cfg.save()

    @staticmethod
    def invalidate(key: str) -> None:
        _cache.pop(key, None)

    @staticmethod
    def _cast(value: str, value_type: str):
        try:
            if value_type == "int":
                return int(value)
            if value_type == "bool":
                return value.lower() in ("true", "1", "yes")
            if value_type == "json":
                return json.loads(value)
            return value
        except (ValueError, json.JSONDecodeError) as e:
            logger.error("ConfigService cast error for value %r as %s: %s", value, value_type, e)
            return value
```

- [ ] **Step 6: Create signals**

Create `apps/config/signals.py`:

```python
from django.db.models.signals import post_save
from django.dispatch import receiver


@receiver(post_save, sender="config.SiteConfig")
def invalidate_config_cache(sender, instance, **kwargs):
    from apps.config.services import ConfigService
    ConfigService.invalidate(instance.key)
```

- [ ] **Step 7: Create admin**

Create `apps/config/admin.py`:

```python
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin

from .models import SiteConfig


@admin.register(SiteConfig)
class SiteConfigAdmin(ModelAdmin):
    list_display = ("key", "value_type", "value", "is_public", "description")
    list_filter = ("value_type", "is_public")
    search_fields = ("key", "description")
    readonly_fields = ("cast_preview",)
    fieldsets = (
        (None, {"fields": ("key", "value_type", "value", "cast_preview")}),
        (_("Metadatos"), {"fields": ("description", "is_public")}),
    )

    @admin.display(description=_("valor interpretado"))
    def cast_preview(self, obj):
        from .services import ConfigService
        return repr(ConfigService._cast(obj.value, obj.value_type))
```

- [ ] **Step 8: Add to LOCAL_APPS (commented)**

In `config/settings/base.py`, replace:

```python
LOCAL_APPS = [
    "apps.core",
    # Agregar apps del proyecto aquí
]
```

with:

```python
LOCAL_APPS = [
    "apps.core",
    # --- v2 optional apps — uncomment to activate ---
    # "apps.notifications",
    # "apps.audit",
    # "apps.config",
    # "apps.permissions",
]
```

- [ ] **Step 9: Activate app and create migration**

Temporarily uncomment `"apps.config"` in `LOCAL_APPS`, then run:

```bash
make makemigrations
```

Expected: `apps/config/migrations/0001_initial.py` created.

Then re-comment the line (will be left commented in the template).

- [ ] **Step 10: Run tests — expect pass**

Temporarily uncomment `"apps.config"` in `LOCAL_APPS`, then:

```bash
make test
```

Expected: all `ConfigService*` and `SiteConfig*` tests PASS.

- [ ] **Step 11: Create README**

Create `apps/config/README.md`:

```markdown
# apps/config

Dynamic site settings stored in the database. Edit values from the admin without touching code.

## Activation

1. Uncomment `"apps.config"` in `LOCAL_APPS` in `config/settings/base.py`
2. Run `make migrate`

## Usage

```python
from apps.config.services import ConfigService

value = ConfigService.get("my_key", default="fallback")
ConfigService.set("my_key", "new_value")
```

## Value types

| Type | Example value | Returns |
|------|--------------|---------|
| `str` | `"Hello"` | `"Hello"` |
| `int` | `"42"` | `42` |
| `bool` | `"true"` | `True` |
| `json` | `'{"a": 1}'` | `{"a": 1}` |

## Template context

Configs with `is_public=True` are available as `public_configs` in templates
once you add `apps.config.context_processors.public_configs` to `TEMPLATES[0]["OPTIONS"]["context_processors"]`.
```

- [ ] **Step 12: Commit**

```bash
git add apps/config/ config/settings/base.py
git commit -m "feat: add apps/config — dynamic site settings

SiteConfig model, ConfigService with in-memory cache, Unfold admin,
signals for cache invalidation, full test suite."
```

---

## Task 2: `apps/audit` — Models, Mixin, Middleware, Signals, Admin, Tests

**Files:**
- Create: `apps/audit/__init__.py`
- Create: `apps/audit/apps.py`
- Create: `apps/audit/models.py`
- Create: `apps/audit/mixins.py`
- Create: `apps/audit/middleware.py`
- Create: `apps/audit/signals.py`
- Create: `apps/audit/admin.py`
- Create: `apps/audit/tests.py`
- Create: `apps/audit/migrations/__init__.py`
- Create: `apps/audit/README.md`

- [ ] **Step 1: Write the failing tests**

Create `apps/audit/tests.py`:

```python
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model

User = get_user_model()


class AuditLogModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="auditor", password="pass")

    def test_create_audit_log(self):
        from apps.audit.models import AuditLog
        log = AuditLog.objects.create(
            user=self.user,
            action=AuditLog.Action.CREATE,
            model_name="core.User",
            object_id="1",
            object_repr="auditor (Traductor)",
        )
        self.assertEqual(str(log), "create — core.User #1")

    def test_audit_log_without_user(self):
        from apps.audit.models import AuditLog
        log = AuditLog.objects.create(
            action=AuditLog.Action.LOGIN,
            model_name="",
            object_repr="system",
        )
        self.assertIsNone(log.user)

    def test_all_actions_valid(self):
        from apps.audit.models import AuditLog
        for action in AuditLog.Action.values:
            log = AuditLog.objects.create(
                action=action,
                model_name="test",
                object_repr="test",
            )
            self.assertEqual(log.action, action)


class AuditLoginSignalTest(TestCase):
    def test_login_creates_audit_log(self):
        from apps.audit.models import AuditLog
        User.objects.create_user(username="loginuser", password="pass")
        self.client.login(username="loginuser", password="pass")
        self.assertTrue(AuditLog.objects.filter(action=AuditLog.Action.LOGIN).exists())

    def test_logout_creates_audit_log(self):
        from apps.audit.models import AuditLog
        User.objects.create_user(username="logoutuser", password="pass")
        self.client.login(username="logoutuser", password="pass")
        self.client.logout()
        self.assertTrue(AuditLog.objects.filter(action=AuditLog.Action.LOGOUT).exists())


class AuditAdminRegisteredTest(TestCase):
    def test_auditlog_registered(self):
        from django.contrib import admin
        from apps.audit.models import AuditLog
        self.assertIn(AuditLog, admin.site._registry)
```

- [ ] **Step 2: Run tests — expect failure**

```bash
make test
```

Expected: `ModuleNotFoundError: No module named 'apps.audit'`

- [ ] **Step 3: Create app scaffold**

Create `apps/audit/__init__.py` (empty).

Create `apps/audit/apps.py`:

```python
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AuditConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.audit"
    verbose_name = _("Auditoría")

    def ready(self):
        import apps.audit.signals  # noqa: F401
```

Create `apps/audit/migrations/__init__.py` (empty).

- [ ] **Step 4: Create the model**

Create `apps/audit/models.py`:

```python
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
```

- [ ] **Step 5: Create signals (login/logout capture)**

Create `apps/audit/signals.py`:

```python
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver


def _get_ip(request):
    x_forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded:
        return x_forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


@receiver(user_logged_in)
def on_login(sender, request, user, **kwargs):
    from apps.audit.models import AuditLog
    AuditLog.objects.create(
        user=user,
        action=AuditLog.Action.LOGIN,
        model_name="",
        object_repr=str(user),
        ip_address=_get_ip(request),
        user_agent=request.META.get("HTTP_USER_AGENT", "")[:300],
    )


@receiver(user_logged_out)
def on_logout(sender, request, user, **kwargs):
    from apps.audit.models import AuditLog
    AuditLog.objects.create(
        user=user,
        action=AuditLog.Action.LOGOUT,
        model_name="",
        object_repr=str(user) if user else "",
        ip_address=_get_ip(request),
        user_agent=request.META.get("HTTP_USER_AGENT", "")[:300],
    )
```

- [ ] **Step 6: Create AuditMixin for ModelAdmin**

Create `apps/audit/mixins.py`:

```python
import json

from django.utils.translation import gettext_lazy as _


class AuditMixin:
    """
    Mix into any unfold.admin.ModelAdmin to automatically log create/update/delete
    actions to AuditLog.

    Usage:
        class MyModelAdmin(AuditMixin, ModelAdmin):
            ...
    """

    def _get_changes(self, original, form):
        changes = {}
        if original is None:
            return None
        for field, new_value in form.cleaned_data.items():
            old_value = getattr(original, field, None)
            if str(old_value) != str(new_value):
                changes[field] = {
                    "before": str(old_value),
                    "after": str(new_value),
                }
        return changes or None

    def save_model(self, request, obj, form, change):
        from apps.audit.models import AuditLog

        is_new = obj.pk is None
        original = None
        if change and obj.pk:
            try:
                original = obj.__class__.objects.get(pk=obj.pk)
            except obj.__class__.DoesNotExist:
                pass

        super().save_model(request, obj, form, change)

        action = AuditLog.Action.UPDATE if change else AuditLog.Action.CREATE
        AuditLog.objects.create(
            user=request.user,
            action=action,
            model_name=f"{obj._meta.app_label}.{obj._meta.model_name}",
            object_id=str(obj.pk),
            object_repr=str(obj),
            changes=self._get_changes(original, form),
            ip_address=request.META.get("REMOTE_ADDR"),
            user_agent=request.META.get("HTTP_USER_AGENT", "")[:300],
        )

    def delete_model(self, request, obj):
        from apps.audit.models import AuditLog

        AuditLog.objects.create(
            user=request.user,
            action=AuditLog.Action.DELETE,
            model_name=f"{obj._meta.app_label}.{obj._meta.model_name}",
            object_id=str(obj.pk),
            object_repr=str(obj),
            ip_address=request.META.get("REMOTE_ADDR"),
            user_agent=request.META.get("HTTP_USER_AGENT", "")[:300],
        )
        super().delete_model(request, obj)
```

- [ ] **Step 7: Create optional middleware**

Create `apps/audit/middleware.py`:

```python
class AuditMiddleware:
    """
    Optional middleware — logs 'view' actions for every authenticated GET request.
    Add to MIDDLEWARE in settings only if needed:
        "apps.audit.middleware.AuditMiddleware"
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if (
            request.method == "GET"
            and request.user.is_authenticated
            and not request.path.startswith("/static/")
        ):
            from apps.audit.models import AuditLog
            x_forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
            ip = x_forwarded.split(",")[0].strip() if x_forwarded else request.META.get("REMOTE_ADDR")
            AuditLog.objects.create(
                user=request.user,
                action=AuditLog.Action.VIEW,
                model_name="",
                object_repr=request.path,
                ip_address=ip,
                user_agent=request.META.get("HTTP_USER_AGENT", "")[:300],
            )
        return response
```

- [ ] **Step 8: Create admin**

Create `apps/audit/admin.py`:

```python
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin

from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(ModelAdmin):
    list_display = ("timestamp", "user", "action", "model_name", "object_repr", "ip_address")
    list_filter = ("action", "model_name", "timestamp")
    search_fields = ("user__username", "object_repr", "model_name", "ip_address")
    date_hierarchy = "timestamp"
    readonly_fields = (
        "user", "action", "model_name", "object_id", "object_repr",
        "changes", "ip_address", "user_agent", "timestamp",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
```

- [ ] **Step 9: Add to LOCAL_APPS (commented) and create migration**

In `config/settings/base.py`, the `LOCAL_APPS` block already has the commented line from Task 1.

Temporarily uncomment `"apps.audit"`, then run:

```bash
make makemigrations
```

Expected: `apps/audit/migrations/0001_initial.py` created. Re-comment the line.

- [ ] **Step 10: Run tests — expect pass**

Temporarily uncomment `"apps.audit"` in `LOCAL_APPS`, then:

```bash
make test
```

Expected: all `AuditLog*` tests PASS.

- [ ] **Step 11: Create README**

Create `apps/audit/README.md`:

```markdown
# apps/audit

Full activity log: admin CRUD, login, logout, and optional navigation tracking.

## Activation

1. Uncomment `"apps.audit"` in `LOCAL_APPS` in `config/settings/base.py`
2. Run `make migrate`

## Admin CRUD tracking

Add `AuditMixin` to any `ModelAdmin` to auto-log create/update/delete:

```python
from apps.audit.mixins import AuditMixin
from unfold.admin import ModelAdmin

class MyModelAdmin(AuditMixin, ModelAdmin):
    ...
```

## Navigation tracking (optional)

Add to `MIDDLEWARE` in `config/settings/base.py`:

```python
"apps.audit.middleware.AuditMiddleware",
```

This logs every authenticated GET request as a `view` action.
```

- [ ] **Step 12: Commit**

```bash
git add apps/audit/
git commit -m "feat: add apps/audit — full activity log

AuditLog model, login/logout signals, AuditMixin for ModelAdmin,
optional AuditMiddleware, read-only Unfold admin, full test suite."
```

---

## Task 3: `apps/notifications` — Models, Service, Admin, Tests

**Files:**
- Create: `apps/notifications/__init__.py`
- Create: `apps/notifications/apps.py`
- Create: `apps/notifications/models.py`
- Create: `apps/notifications/services.py`
- Create: `apps/notifications/signals.py`
- Create: `apps/notifications/admin.py`
- Create: `apps/notifications/tests.py`
- Create: `apps/notifications/migrations/__init__.py`
- Create: `apps/notifications/README.md`

- [ ] **Step 1: Write the failing tests**

Create `apps/notifications/tests.py`:

```python
import hashlib
import hmac
from unittest.mock import patch, MagicMock

from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class NotificationModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="recipient", password="pass")

    def test_create_in_app_notification(self):
        from apps.notifications.models import Notification
        n = Notification.objects.create(
            recipient=self.user,
            title="Test",
            body="Body",
            channel=Notification.Channel.IN_APP,
        )
        self.assertIsNone(n.read_at)
        self.assertIsNone(n.sent_at)

    def test_str_includes_title(self):
        from apps.notifications.models import Notification
        n = Notification.objects.create(
            recipient=self.user,
            title="Hello",
            body="World",
            channel=Notification.Channel.IN_APP,
        )
        self.assertIn("Hello", str(n))

    def test_webhook_endpoint_str(self):
        from apps.notifications.models import WebhookEndpoint
        ep = WebhookEndpoint.objects.create(
            user=self.user,
            url="https://example.com/hook",
            secret="mysecret",
        )
        self.assertIn("example.com", str(ep))


class NotificationServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="notif_user",
            email="notif@example.com",
            password="pass",
        )

    def test_send_in_app_creates_record(self):
        from apps.notifications.services import NotificationService
        from apps.notifications.models import Notification
        NotificationService.send(
            user=self.user,
            title="Welcome",
            body="Hello!",
            channels=["in_app"],
        )
        self.assertTrue(
            Notification.objects.filter(recipient=self.user, title="Welcome").exists()
        )

    @patch("apps.notifications.services.send_mail")
    def test_send_email_calls_send_mail(self, mock_send):
        from apps.notifications.services import NotificationService
        NotificationService.send(
            user=self.user,
            title="Email Alert",
            body="Check this out",
            channels=["email"],
        )
        mock_send.assert_called_once()
        call_kwargs = mock_send.call_args
        self.assertIn("notif@example.com", call_kwargs[1].get("recipient_list", []) or call_kwargs[0][3])

    @patch("apps.notifications.services.requests.post")
    def test_send_webhook_posts_to_endpoint(self, mock_post):
        from apps.notifications.models import WebhookEndpoint
        from apps.notifications.services import NotificationService
        mock_post.return_value = MagicMock(status_code=200)
        WebhookEndpoint.objects.create(
            user=self.user,
            url="https://example.com/hook",
            secret="secret123",
            is_active=True,
        )
        NotificationService.send(
            user=self.user,
            title="Hook",
            body="Fired",
            channels=["webhook"],
            payload={"event": "test"},
        )
        mock_post.assert_called_once()

    @patch("apps.notifications.services.requests.post")
    def test_webhook_signature_header_present(self, mock_post):
        from apps.notifications.models import WebhookEndpoint
        from apps.notifications.services import NotificationService
        mock_post.return_value = MagicMock(status_code=200)
        WebhookEndpoint.objects.create(
            user=self.user,
            url="https://hook.example.com/",
            secret="topsecret",
            is_active=True,
        )
        NotificationService.send(
            user=self.user,
            title="Signed",
            body="Payload",
            channels=["webhook"],
            payload={"x": 1},
        )
        headers = mock_post.call_args[1].get("headers", {})
        self.assertIn("X-Signature", headers)


class NotificationAdminRegisteredTest(TestCase):
    def test_notification_registered(self):
        from django.contrib import admin
        from apps.notifications.models import Notification
        self.assertIn(Notification, admin.site._registry)

    def test_webhook_endpoint_registered(self):
        from django.contrib import admin
        from apps.notifications.models import WebhookEndpoint
        self.assertIn(WebhookEndpoint, admin.site._registry)
```

- [ ] **Step 2: Run tests — expect failure**

```bash
make test
```

Expected: `ModuleNotFoundError: No module named 'apps.notifications'`

- [ ] **Step 3: Create app scaffold**

Create `apps/notifications/__init__.py` (empty).

Create `apps/notifications/apps.py`:

```python
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class NotificationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.notifications"
    verbose_name = _("Notificaciones")

    def ready(self):
        import apps.notifications.signals  # noqa: F401
```

Create `apps/notifications/migrations/__init__.py` (empty).

Create `apps/notifications/signals.py` (empty for now — reserved for cross-app triggers):

```python
# Cross-app signal handlers — connect here to avoid circular imports.
```

- [ ] **Step 4: Create models**

Create `apps/notifications/models.py`:

```python
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
```

- [ ] **Step 5: Create service**

Create `apps/notifications/services.py`:

```python
import hashlib
import hmac
import json
import logging
from datetime import datetime, timezone

import requests
from django.core.mail import send_mail
from django.conf import settings
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)


class NotificationService:
    @staticmethod
    def send(user, title: str, body: str, channels: list, payload: dict = None) -> None:
        payload = payload or {}
        for channel in channels:
            try:
                if channel == "in_app":
                    NotificationService._send_in_app(user, title, body, payload)
                elif channel == "email":
                    NotificationService._send_email(user, title, body)
                elif channel == "webhook":
                    NotificationService._send_webhook(user, title, body, payload)
            except Exception as e:
                logger.error("NotificationService error on channel %s for user %s: %s", channel, user, e)

    @staticmethod
    def _send_in_app(user, title, body, payload):
        from apps.notifications.models import Notification
        Notification.objects.create(
            recipient=user,
            title=title,
            body=body,
            channel="in_app",
            payload=payload,
            sent_at=datetime.now(tz=timezone.utc),
        )

    @staticmethod
    def _send_email(user, title, body):
        from apps.notifications.models import Notification
        send_mail(
            subject=title,
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        Notification.objects.create(
            recipient=user,
            title=title,
            body=body,
            channel="email",
            sent_at=datetime.now(tz=timezone.utc),
        )

    @staticmethod
    def _send_webhook(user, title, body, payload):
        from apps.notifications.models import Notification, WebhookEndpoint
        endpoints = WebhookEndpoint.objects.filter(user=user, is_active=True)
        for endpoint in endpoints:
            data = {"title": title, "body": body, **payload}
            body_bytes = json.dumps(data).encode("utf-8")
            signature = hmac.new(
                endpoint.secret.encode("utf-8"),
                body_bytes,
                hashlib.sha256,
            ).hexdigest()
            try:
                response = requests.post(
                    endpoint.url,
                    data=body_bytes,
                    headers={
                        "Content-Type": "application/json",
                        "X-Signature": f"sha256={signature}",
                    },
                    timeout=5,
                )
                Notification.objects.create(
                    recipient=user,
                    title=title,
                    body=body,
                    channel="webhook",
                    payload=payload,
                    sent_at=datetime.now(tz=timezone.utc),
                )
            except requests.RequestException as e:
                logger.error("Webhook POST failed to %s: %s", endpoint.url, e)
```

- [ ] **Step 6: Create admin**

Create `apps/notifications/admin.py`:

```python
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
        return obj is None  # allow list but not form edit


@admin.register(WebhookEndpoint)
class WebhookEndpointAdmin(ModelAdmin):
    list_display = ("url", "user", "is_active")
    list_filter = ("is_active",)
    search_fields = ("url", "user__username")
```

- [ ] **Step 7: Create migration**

Temporarily uncomment `"apps.notifications"` in `LOCAL_APPS`, then:

```bash
make makemigrations
```

Expected: `apps/notifications/migrations/0001_initial.py` created. Re-comment the line.

- [ ] **Step 8: Run tests — expect pass**

Temporarily uncomment `"apps.notifications"`, then:

```bash
make test
```

Expected: all `Notification*` and `WebhookEndpoint*` tests PASS.

- [ ] **Step 9: Create README**

Create `apps/notifications/README.md`:

```markdown
# apps/notifications

Send notifications via in-app, email, and webhook channels.

## Activation

1. Uncomment `"apps.notifications"` in `LOCAL_APPS` in `config/settings/base.py`
2. Run `make migrate`

## Usage

```python
from apps.notifications.services import NotificationService

NotificationService.send(
    user=request.user,
    title="Nueva tarea asignada",
    body="Tienes una nueva tarea pendiente.",
    channels=["in_app", "email"],
)

# With webhook payload:
NotificationService.send(
    user=user,
    title="Evento",
    body="Descripción",
    channels=["webhook"],
    payload={"event_type": "task.assigned", "task_id": 42},
)
```

## Webhook signing

Webhooks are signed with HMAC-SHA256. The signature is sent in the `X-Signature` header as `sha256=<hex>`.
Configure each user's endpoint secret in `WebhookEndpoint.secret`.
```

- [ ] **Step 10: Commit**

```bash
git add apps/notifications/
git commit -m "feat: add apps/notifications — in-app, email, webhook notifications

Notification and WebhookEndpoint models, NotificationService with
HMAC-signed webhooks, Unfold admin, full test suite."
```

---

## Task 4: `apps/permissions` — Models, Fixtures, Admin, Tests

**Files:**
- Create: `apps/permissions/__init__.py`
- Create: `apps/permissions/apps.py`
- Create: `apps/permissions/models.py`
- Create: `apps/permissions/admin.py`
- Create: `apps/permissions/signals.py`
- Create: `apps/permissions/tests.py`
- Create: `apps/permissions/migrations/__init__.py`
- Create: `apps/permissions/migrations/0002_default_roles.py`
- Create: `apps/permissions/fixtures/default_roles.json`
- Create: `apps/permissions/README.md`

- [ ] **Step 1: Write the failing tests**

Create `apps/permissions/tests.py`:

```python
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType

User = get_user_model()


class RoleModelTest(TestCase):
    def test_create_role(self):
        from apps.permissions.models import Role
        role = Role.objects.create(name="editor", description="Puede editar contenido")
        self.assertEqual(str(role), "editor")

    def test_role_name_unique(self):
        from apps.permissions.models import Role
        from django.db import IntegrityError
        Role.objects.create(name="unique_role")
        with self.assertRaises(IntegrityError):
            Role.objects.create(name="unique_role")


class UserRoleTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="roleuser", password="pass")
        from apps.permissions.models import Role
        self.role = Role.objects.create(name="tester")

    def test_assign_role_to_user(self):
        from apps.permissions.models import UserRole
        ur = UserRole.objects.create(user=self.user, role=self.role)
        self.assertEqual(ur.user, self.user)
        self.assertEqual(ur.role, self.role)

    def test_user_roles_relation(self):
        from apps.permissions.models import UserRole
        UserRole.objects.create(user=self.user, role=self.role)
        self.assertIn(self.role, self.user.assigned_roles.all())


class ObjectPermissionTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="objperm_user", password="pass")
        self.ct = ContentType.objects.get_for_model(User)
        from django.contrib.auth.models import Permission
        self.perm = Permission.objects.filter(content_type=self.ct).first()

    def test_create_object_permission(self):
        from apps.permissions.models import ObjectPermission
        op = ObjectPermission.objects.create(
            user=self.user,
            content_type=self.ct,
            object_id=str(self.user.pk),
            permission=self.perm,
        )
        self.assertEqual(op.user, self.user)


class PermissionsAdminRegisteredTest(TestCase):
    def test_role_registered(self):
        from django.contrib import admin
        from apps.permissions.models import Role
        self.assertIn(Role, admin.site._registry)
```

- [ ] **Step 2: Run tests — expect failure**

```bash
make test
```

Expected: `ModuleNotFoundError: No module named 'apps.permissions'`

- [ ] **Step 3: Create app scaffold**

Create `apps/permissions/__init__.py` (empty).

Create `apps/permissions/apps.py`:

```python
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class PermissionsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.permissions"
    verbose_name = _("Permisos y roles")

    def ready(self):
        import apps.permissions.signals  # noqa: F401
```

Create `apps/permissions/migrations/__init__.py` (empty).

Create `apps/permissions/signals.py` (empty — reserved):

```python
# Reserved for cross-app signal handlers.
```

- [ ] **Step 4: Create models**

Create `apps/permissions/models.py`:

```python
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


# Add reverse relation to User for convenience
from django.contrib.auth import get_user_model  # noqa: E402

def _add_assigned_roles():
    User = get_user_model()
    if not hasattr(User, "assigned_roles"):
        User.add_to_class(
            "assigned_roles",
            models.ManyToManyField(
                Role,
                through=UserRole,
                related_name="users",
                blank=True,
                verbose_name=_("roles asignados"),
            ),
        )

_add_assigned_roles()


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
```

- [ ] **Step 5: Create admin**

Create `apps/permissions/admin.py`:

```python
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin, TabularInline

from .models import ObjectPermission, Role, UserRole


class UserRoleInline(TabularInline):
    model = UserRole
    extra = 0
    fields = ("role", "assigned_by", "assigned_at")
    readonly_fields = ("assigned_at",)
    verbose_name = _("rol asignado")
    verbose_name_plural = _("roles asignados")


@admin.register(Role)
class RoleAdmin(ModelAdmin):
    list_display = ("name", "description", "user_count")
    search_fields = ("name", "description")
    filter_horizontal = ("permissions",)

    @admin.display(description=_("usuarios"))
    def user_count(self, obj):
        return obj.user_roles.count()


@admin.register(UserRole)
class UserRoleAdmin(ModelAdmin):
    list_display = ("user", "role", "assigned_by", "assigned_at")
    list_filter = ("role",)
    search_fields = ("user__username", "role__name")
    readonly_fields = ("assigned_at",)


@admin.register(ObjectPermission)
class ObjectPermissionAdmin(ModelAdmin):
    list_display = ("user", "content_type", "object_id", "permission")
    list_filter = ("content_type",)
    search_fields = ("user__username", "object_id")
```

- [ ] **Step 6: Create migration and fixtures**

Temporarily uncomment `"apps.permissions"` in `LOCAL_APPS`, then:

```bash
make makemigrations
```

Expected: `apps/permissions/migrations/0001_initial.py` created.

Create `apps/permissions/fixtures/default_roles.json`:

```json
[
  {
    "model": "permissions.role",
    "pk": 1,
    "fields": {
      "name": "admin",
      "description": "Administrador del sistema",
      "permissions": []
    }
  },
  {
    "model": "permissions.role",
    "pk": 2,
    "fields": {
      "name": "pm",
      "description": "Project Manager",
      "permissions": []
    }
  },
  {
    "model": "permissions.role",
    "pk": 3,
    "fields": {
      "name": "translator",
      "description": "Traductor",
      "permissions": []
    }
  },
  {
    "model": "permissions.role",
    "pk": 4,
    "fields": {
      "name": "reviewer",
      "description": "Revisor",
      "permissions": []
    }
  }
]
```

Re-comment the line.

- [ ] **Step 7: Run tests — expect pass**

Temporarily uncomment `"apps.permissions"`, then:

```bash
make test
```

Expected: all `Role*`, `UserRole*`, `ObjectPermission*` tests PASS.

- [ ] **Step 8: Create README**

Create `apps/permissions/README.md`:

```markdown
# apps/permissions

Granular role and per-object permission management.

## Activation

1. Uncomment `"apps.permissions"` in `LOCAL_APPS` in `config/settings/base.py`
2. Run `make migrate`
3. Load default roles: `docker compose -f docker-compose.dev.yml exec app_web_dev python manage.py loaddata apps/permissions/fixtures/default_roles.json`

## Roles

Roles group Django permissions and are assigned to users via `UserRole`.
The default roles (`admin`, `pm`, `translator`, `reviewer`) match the string roles in `core.User`.

## Per-object permissions

`ObjectPermission` grants a specific user permission on a specific model instance:

```python
from apps.permissions.models import ObjectPermission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission

ObjectPermission.objects.create(
    user=user,
    content_type=ContentType.objects.get_for_model(MyModel),
    object_id=str(instance.pk),
    permission=Permission.objects.get(codename="change_mymodel"),
)
```
```

- [ ] **Step 9: Commit**

```bash
git add apps/permissions/
git commit -m "feat: add apps/permissions — roles and per-object permissions

Role, UserRole, ObjectPermission models, default fixtures matching
v1 string roles, Unfold admin with inline UserRole, full test suite."
```

---

## Task 5: Update `CLAUDE.md` and `config/settings/base.py`

**Files:**
- Modify: `CLAUDE.md`
- Modify: `config/settings/base.py` (verify LOCAL_APPS comment block is present)

- [ ] **Step 1: Add v2 section to CLAUDE.md**

Open `CLAUDE.md` and append the following section after the existing content:

```markdown
## Apps v2 — Módulos opcionales

Activar cualquier app v2:
1. Descomentar la app en `LOCAL_APPS` en `config/settings/base.py`
2. Ejecutar `make migrate`

### apps/config — Configuración dinámica

```python
from apps.config.services import ConfigService

value = ConfigService.get("mi_clave", default="fallback")
ConfigService.set("mi_clave", "nuevo_valor")
```

### apps/audit — Registro de auditoría

Agregar `AuditMixin` a cualquier `ModelAdmin` para auto-registrar CRUD:

```python
from apps.audit.mixins import AuditMixin
from unfold.admin import ModelAdmin

class MiModelAdmin(AuditMixin, ModelAdmin):
    ...
```

Para rastrear navegación, agregar a `MIDDLEWARE`:
```python
"apps.audit.middleware.AuditMiddleware",
```

### apps/notifications — Notificaciones

```python
from apps.notifications.services import NotificationService

NotificationService.send(
    user=user,
    title="Asunto",
    body="Mensaje",
    channels=["in_app", "email", "webhook"],
    payload={"key": "value"},  # solo para webhook
)
```

### apps/permissions — Roles y permisos

Cargar roles por defecto tras migrar:
```bash
docker compose -f docker-compose.dev.yml exec app_web_dev python manage.py loaddata apps/permissions/fixtures/default_roles.json
```

## Reglas transversales v2

- Todo `ModelAdmin` hereda de `unfold.admin.ModelAdmin`.
- Todo string de UI en `_()` o `{% trans %}` desde el primer commit.
- Traducciones centralizadas en `locale/es/` y `locale/en/` (raíz del proyecto).
- Lógica de negocio solo en clases `*Service`, nunca en vistas o admin.
```

- [ ] **Step 2: Commit**

```bash
git add CLAUDE.md config/settings/base.py
git commit -m "docs: update CLAUDE.md with v2 apps documentation

Add activation instructions, service usage patterns, AuditMixin
usage, and transversal constraints for all v2 apps."
```

---

## Task 6: Generate translation files

**Files:**
- Create/update: `locale/es/LC_MESSAGES/django.po`
- Create/update: `locale/en/LC_MESSAGES/django.po`

- [ ] **Step 1: Activate all v2 apps**

In `config/settings/base.py`, uncomment all four v2 apps:

```python
LOCAL_APPS = [
    "apps.core",
    "apps.notifications",
    "apps.audit",
    "apps.config",
    "apps.permissions",
]
```

- [ ] **Step 2: Run makemessages**

```bash
make messages
```

Expected: `locale/es/LC_MESSAGES/django.po` and `locale/en/LC_MESSAGES/django.po` updated with all new strings from v2 apps.

- [ ] **Step 3: Add English translations**

Open `locale/en/LC_MESSAGES/django.po` and fill in `msgstr` for all new v2 strings. Key translations:

```po
msgid "Configuración"
msgstr "Configuration"

msgid "configuración del sitio"
msgstr "site configuration"

msgid "configuraciones del sitio"
msgstr "site configurations"

msgid "clave"
msgstr "key"

msgid "valor"
msgstr "value"

msgid "tipo de valor"
msgstr "value type"

msgid "descripción"
msgstr "description"

msgid "pública"
msgstr "public"

msgid "valor interpretado"
msgstr "interpreted value"

msgid "Auditoría"
msgstr "Audit"

msgid "registro de auditoría"
msgstr "audit log"

msgid "registros de auditoría"
msgstr "audit logs"

msgid "acción"
msgstr "action"

msgid "modelo"
msgstr "model"

msgid "ID objeto"
msgstr "object ID"

msgid "representación del objeto"
msgstr "object representation"

msgid "cambios"
msgstr "changes"

msgid "dirección IP"
msgstr "IP address"

msgid "user agent"
msgstr "user agent"

msgid "fecha y hora"
msgstr "date and time"

msgid "Notificaciones"
msgstr "Notifications"

msgid "notificación"
msgstr "notification"

msgid "notificaciones"
msgstr "notifications"

msgid "destinatario"
msgstr "recipient"

msgid "título"
msgstr "title"

msgid "cuerpo"
msgstr "body"

msgid "canal"
msgstr "channel"

msgid "leída el"
msgstr "read at"

msgid "enviada el"
msgstr "sent at"

msgid "payload"
msgstr "payload"

msgid "creada el"
msgstr "created at"

msgid "endpoint webhook"
msgstr "webhook endpoint"

msgid "endpoints webhook"
msgstr "webhook endpoints"

msgid "secreto"
msgstr "secret"

msgid "activo"
msgstr "active"

msgid "Permisos y roles"
msgstr "Permissions and roles"

msgid "rol"
msgstr "role"

msgid "roles"
msgstr "roles"

msgid "nombre"
msgstr "name"

msgid "permisos"
msgstr "permissions"

msgid "rol de usuario"
msgstr "user role"

msgid "roles de usuario"
msgstr "user roles"

msgid "asignado el"
msgstr "assigned at"

msgid "asignado por"
msgstr "assigned by"

msgid "roles asignados"
msgstr "assigned roles"

msgid "permiso por objeto"
msgstr "object permission"

msgid "permisos por objeto"
msgstr "object permissions"

msgid "tipo de contenido"
msgstr "content type"

msgid "ID del objeto"
msgstr "object ID"

msgid "usuarios"
msgstr "users"
```

- [ ] **Step 4: Compile translations**

```bash
make compilemessages
```

Expected: `.mo` files generated without errors.

- [ ] **Step 5: Run full test suite**

```bash
make test
```

Expected: all tests PASS with all four v2 apps active.

- [ ] **Step 6: Re-comment v2 apps in settings (template default)**

In `config/settings/base.py`, re-comment the v2 apps so the template ships with them inactive:

```python
LOCAL_APPS = [
    "apps.core",
    # --- v2 optional apps — uncomment to activate ---
    # "apps.notifications",
    # "apps.audit",
    # "apps.config",
    # "apps.permissions",
]
```

- [ ] **Step 7: Commit**

```bash
git add locale/ config/settings/base.py
git commit -m "i18n: add es/en translations for all v2 apps

All UI strings in notifications, audit, config, permissions
translated to Spanish and English."
```

---

## Done

All four v2 apps implemented. Verify final state:

- [ ] `make test` passes with all apps active
- [ ] `apps/config/README.md`, `apps/audit/README.md`, `apps/notifications/README.md`, `apps/permissions/README.md` exist
- [ ] `CLAUDE.md` has v2 section
- [ ] `config/settings/base.py` has all four apps commented out (template default)
- [ ] `locale/` has compiled `.mo` files
