# Plugin System — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Que agregar una app v2 al proyecto solo requiera una línea en `LOCAL_APPS` — URLs, middleware y settings se auto-registran desde el `AppConfig` de la app.

**Architecture:** Un módulo `config/plugins.py` itera `INSTALLED_APPS` después de que Django los define, lee atributos opcionales (`plugin_urls`, `plugin_middleware`, `plugin_settings`) de cada `AppConfig`, y aplica los cambios a `MIDDLEWARE` y `globals()` de `base.py`. Las URLs resultantes se exponen como `_plugin_urls` y se consumen en `config/urls.py`.

**Tech Stack:** Django 6, Python 3.12, pytest/Django test runner, AppConfig API.

---

## File Map

| Archivo | Acción | Responsabilidad |
|---------|--------|-----------------|
| `config/plugins.py` | Crear | Motor de auto-registro |
| `config/tests_plugins.py` | Crear | Tests del motor (sin DB) |
| `config/settings/base.py` | Modificar | Llamar `autoregister_plugins()` al final |
| `config/urls.py` | Modificar | Consumir `_plugin_urls` en lugar de path hardcodeado |
| `apps/notifications/apps.py` | Modificar | Declarar `plugin_urls` y `plugin_settings` |
| `apps/audit/apps.py` | Modificar | Declarar `plugin_middleware` |

---

### Task 1: Motor de auto-registro (`config/plugins.py`)

**Files:**
- Create: `config/plugins.py`

- [ ] **Step 1: Crear `config/plugins.py`**

```python
from django.apps import apps as django_apps


def autoregister_plugins(installed_apps, middleware, settings_module):
    """Read plugin_* attributes from each AppConfig and apply them."""
    url_patterns = []

    for app_label in installed_apps:
        try:
            config = django_apps.get_app_config(_app_name(app_label))
        except LookupError:
            continue

        for url_def in getattr(config, "plugin_urls", []):
            url_patterns.append(url_def)

        for mw_def in getattr(config, "plugin_middleware", []):
            _insert_middleware(middleware, mw_def)

        for key, value in getattr(config, "plugin_settings", {}).items():
            if key not in settings_module:
                settings_module[key] = value

    return url_patterns


def _app_name(app_label):
    return app_label.split(".")[-1] if "." in app_label else app_label


def _insert_middleware(middleware, mw_def):
    target = mw_def["middleware"]
    if target in middleware:
        return
    after = mw_def.get("insert_after")
    if after:
        for i, mw in enumerate(middleware):
            if after in mw:
                middleware.insert(i + 1, target)
                return
    middleware.append(target)
```

- [ ] **Step 2: Commit**

```bash
git add config/plugins.py
git commit -m "feat: add plugin auto-registration engine"
```

---

### Task 2: Tests del motor (`config/tests_plugins.py`)

**Files:**
- Create: `config/tests_plugins.py`

Los tests usan `unittest.TestCase` puro — no necesitan DB ni Django setup completo. Se llama `autoregister_plugins` con listas y dicts ficticios, sin tocar AppConfig real.

- [ ] **Step 1: Escribir los tests**

```python
from unittest import TestCase
from unittest.mock import MagicMock, patch

from config.plugins import autoregister_plugins, _insert_middleware


class TestInsertMiddleware(TestCase):
    def test_insert_after_known_middleware(self):
        middleware = [
            "django.contrib.sessions.middleware.SessionMiddleware",
            "django.contrib.auth.middleware.AuthenticationMiddleware",
            "django.contrib.messages.middleware.MessageMiddleware",
        ]
        _insert_middleware(middleware, {
            "middleware": "apps.audit.middleware.AuditMiddleware",
            "insert_after": "AuthenticationMiddleware",
        })
        auth_idx = middleware.index("django.contrib.auth.middleware.AuthenticationMiddleware")
        audit_idx = middleware.index("apps.audit.middleware.AuditMiddleware")
        self.assertEqual(audit_idx, auth_idx + 1)

    def test_no_duplicate(self):
        middleware = ["apps.audit.middleware.AuditMiddleware"]
        _insert_middleware(middleware, {
            "middleware": "apps.audit.middleware.AuditMiddleware",
            "insert_after": "AuthenticationMiddleware",
        })
        self.assertEqual(middleware.count("apps.audit.middleware.AuditMiddleware"), 1)

    def test_append_when_insert_after_not_found(self):
        middleware = ["django.middleware.common.CommonMiddleware"]
        _insert_middleware(middleware, {
            "middleware": "apps.audit.middleware.AuditMiddleware",
            "insert_after": "NonExistentMiddleware",
        })
        self.assertEqual(middleware[-1], "apps.audit.middleware.AuditMiddleware")

    def test_append_when_no_insert_after(self):
        middleware = ["django.middleware.common.CommonMiddleware"]
        _insert_middleware(middleware, {
            "middleware": "apps.audit.middleware.AuditMiddleware",
        })
        self.assertEqual(middleware[-1], "apps.audit.middleware.AuditMiddleware")


class TestAutoregisterPlugins(TestCase):
    def _make_config(self, name, plugin_urls=None, plugin_middleware=None, plugin_settings=None):
        config = MagicMock()
        config.name = name
        if plugin_urls is not None:
            config.plugin_urls = plugin_urls
        else:
            del config.plugin_urls
        if plugin_middleware is not None:
            config.plugin_middleware = plugin_middleware
        else:
            del config.plugin_middleware
        if plugin_settings is not None:
            config.plugin_settings = plugin_settings
        else:
            del config.plugin_settings
        return config

    def test_urls_registered(self):
        fake_config = self._make_config(
            "notifications",
            plugin_urls=[{"prefix": "admin/notifications/", "urlconf": "apps.notifications.urls"}],
        )
        middleware = []
        settings_module = {}

        with patch("config.plugins.django_apps.get_app_config", return_value=fake_config):
            urls = autoregister_plugins(["apps.notifications"], middleware, settings_module)

        self.assertEqual(len(urls), 1)
        self.assertEqual(urls[0]["prefix"], "admin/notifications/")

    def test_middleware_inserted(self):
        fake_config = self._make_config(
            "audit",
            plugin_middleware=[{
                "middleware": "apps.audit.middleware.AuditMiddleware",
                "insert_after": "AuthenticationMiddleware",
            }],
        )
        middleware = ["django.contrib.auth.middleware.AuthenticationMiddleware"]
        settings_module = {}

        with patch("config.plugins.django_apps.get_app_config", return_value=fake_config):
            autoregister_plugins(["apps.audit"], middleware, settings_module)

        self.assertIn("apps.audit.middleware.AuditMiddleware", middleware)

    def test_settings_not_overwrite(self):
        fake_config = self._make_config(
            "notifications",
            plugin_settings={"WEBHOOK_SECRET": "from-plugin"},
        )
        middleware = []
        settings_module = {"WEBHOOK_SECRET": "already-set"}

        with patch("config.plugins.django_apps.get_app_config", return_value=fake_config):
            autoregister_plugins(["apps.notifications"], middleware, settings_module)

        self.assertEqual(settings_module["WEBHOOK_SECRET"], "already-set")

    def test_settings_injected_when_missing(self):
        fake_config = self._make_config(
            "notifications",
            plugin_settings={"WEBHOOK_SECRET": "from-plugin"},
        )
        middleware = []
        settings_module = {}

        with patch("config.plugins.django_apps.get_app_config", return_value=fake_config):
            autoregister_plugins(["apps.notifications"], middleware, settings_module)

        self.assertEqual(settings_module["WEBHOOK_SECRET"], "from-plugin")

    def test_app_without_attributes_no_error(self):
        fake_config = self._make_config("core")
        middleware = []
        settings_module = {}

        with patch("config.plugins.django_apps.get_app_config", return_value=fake_config):
            urls = autoregister_plugins(["apps.core"], middleware, settings_module)

        self.assertEqual(urls, [])
        self.assertEqual(middleware, [])
        self.assertEqual(settings_module, {})

    def test_unknown_app_skipped(self):
        with patch("config.plugins.django_apps.get_app_config", side_effect=LookupError):
            urls = autoregister_plugins(["apps.nonexistent"], [], {})
        self.assertEqual(urls, [])
```

- [ ] **Step 2: Correr los tests para verificar que fallan correctamente**

```bash
docker compose -f docker-compose.dev.yml exec web_dev python -m pytest config/tests_plugins.py -v
```

Esperado: PASS en todos (los tests usan mocks, no dependen de implementación futura).

- [ ] **Step 3: Commit**

```bash
git add config/tests_plugins.py
git commit -m "test: add plugin engine unit tests"
```

---

### Task 3: Declarar plugin en `apps/notifications/apps.py`

**Files:**
- Modify: `apps/notifications/apps.py`

- [ ] **Step 1: Actualizar `NotificationsConfig`**

Reemplazar el contenido completo de `apps/notifications/apps.py`:

```python
import os

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class NotificationsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.notifications"
    verbose_name = _("Notificaciones")

    plugin_urls = [
        {"prefix": "admin/notifications/", "urlconf": "apps.notifications.urls"},
    ]
    plugin_middleware = []
    plugin_settings = {
        "WEBHOOK_SECRET": os.getenv("WEBHOOK_SECRET", ""),
    }

    def ready(self):
        import apps.notifications.signals  # noqa: F401
```

- [ ] **Step 2: Commit**

```bash
git add apps/notifications/apps.py
git commit -m "feat(notifications): declare plugin_urls and plugin_settings in AppConfig"
```

---

### Task 4: Declarar plugin en `apps/audit/apps.py`

**Files:**
- Modify: `apps/audit/apps.py`

- [ ] **Step 1: Actualizar `AuditConfig`**

Reemplazar el contenido completo de `apps/audit/apps.py`:

```python
from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class AuditConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.audit"
    verbose_name = _("Auditoría")

    plugin_urls = []
    plugin_middleware = [
        {
            "middleware": "apps.audit.middleware.AuditMiddleware",
            "insert_after": "django.contrib.auth.middleware.AuthenticationMiddleware",
        }
    ]
    plugin_settings = {}

    def ready(self):
        import apps.audit.signals  # noqa: F401
```

- [ ] **Step 2: Commit**

```bash
git add apps/audit/apps.py
git commit -m "feat(audit): declare plugin_middleware in AppConfig"
```

---

### Task 5: Integrar en `config/settings/base.py`

**Files:**
- Modify: `config/settings/base.py`

- [ ] **Step 1: Añadir llamada a `autoregister_plugins` al final de `base.py`**

Al final del archivo (después del bloque `UNFOLD = {...}`), añadir:

```python
# --- Plugin auto-registration ---
# Must run after INSTALLED_APPS and MIDDLEWARE are fully defined.
from config.plugins import autoregister_plugins  # noqa: E402

_plugin_urls = autoregister_plugins(INSTALLED_APPS, MIDDLEWARE, globals())
```

- [ ] **Step 2: Verificar que Django arranca sin errores**

```bash
docker compose -f docker-compose.dev.yml exec web_dev python manage.py check
```

Esperado: `System check identified no issues (0 silenced).`

- [ ] **Step 3: Commit**

```bash
git add config/settings/base.py
git commit -m "feat: integrate plugin auto-registration in base settings"
```

---

### Task 6: Actualizar `config/urls.py` para consumir `_plugin_urls`

**Files:**
- Modify: `config/urls.py`

- [ ] **Step 1: Reemplazar el path hardcodeado de notifications**

Reemplazar el contenido completo de `config/urls.py`:

```python
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from apps.core.forms import PlatformAuthenticationForm
from apps.core.views import solicitar_acceso
from config.settings.base import _plugin_urls

admin.site.login_form = PlatformAuthenticationForm

urlpatterns = [
    path("i18n/", include("django.conf.urls.i18n")),
    path("admin/password_reset/", auth_views.PasswordResetView.as_view(), name="admin_password_reset"),
    path("admin/password_reset/done/", auth_views.PasswordResetDoneView.as_view(), name="password_reset_done"),
    path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("reset/done/", auth_views.PasswordResetCompleteView.as_view(), name="password_reset_complete"),
    path("admin/", admin.site.urls),
    path("solicitar-acceso/", solicitar_acceso, name="request_access"),
    # Agregar URLs fijas específicas del proyecto aquí
] + [
    path(u["prefix"], include(u["urlconf"]))
    for u in _plugin_urls
]
```

- [ ] **Step 2: Verificar que las URLs de notifications siguen funcionando**

```bash
docker compose -f docker-compose.dev.yml exec web_dev python manage.py show_urls | grep notifications
```

Esperado: ver `admin/notifications/unread-count/`, `admin/notifications/unread-list/`, `admin/notifications/mark-read/`.

- [ ] **Step 3: Correr los tests existentes de notifications**

```bash
docker compose -f docker-compose.dev.yml exec web_dev python manage.py test apps.notifications -v 2
```

Esperado: todos los tests pasan.

- [ ] **Step 4: Commit**

```bash
git add config/urls.py
git commit -m "feat: consume plugin_urls dynamically in urls.py"
```

---

### Task 7: Verificación de integración completa

- [ ] **Step 1: Correr todos los tests del proyecto**

```bash
docker compose -f docker-compose.dev.yml exec web_dev python manage.py test
```

Esperado: todos los tests pasan.

- [ ] **Step 2: Verificar que `AuditMiddleware` está en MIDDLEWARE**

```bash
docker compose -f docker-compose.dev.yml exec web_dev python manage.py shell -c "from django.conf import settings; print([m for m in settings.MIDDLEWARE if 'audit' in m.lower()])"
```

Esperado: `['apps.audit.middleware.AuditMiddleware']`

- [ ] **Step 3: Verificar que `WEBHOOK_SECRET` está en settings**

```bash
docker compose -f docker-compose.dev.yml exec web_dev python manage.py shell -c "from django.conf import settings; print(hasattr(settings, 'WEBHOOK_SECRET'))"
```

Esperado: `True`

- [ ] **Step 4: Commit final**

```bash
git add .
git commit -m "chore: verify plugin system integration complete"
```

---

## Cómo usar el sistema una vez implementado

Para agregar cualquier nueva app como plugin:

1. Copiar la carpeta en `apps/`
2. Añadir `"apps.mi_app"` en `LOCAL_APPS` en `config/settings/base.py`
3. En `apps/mi_app/apps.py`, declarar `plugin_urls`, `plugin_middleware`, `plugin_settings` según necesidad
4. Ejecutar `make migrate`

No se toca ningún otro archivo del proyecto.
