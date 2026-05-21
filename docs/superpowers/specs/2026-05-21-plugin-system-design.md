# Plugin System para apps v2

**Fecha:** 2026-05-21  
**Estado:** Aprobado

## Objetivo

Que una app v2 se active con una sola línea en `LOCAL_APPS`. URLs, middleware y settings propios se auto-registran desde dentro de la app, sin tocar `config/urls.py`, `MIDDLEWARE`, ni `base.py` manualmente.

## Decisiones clave

| Decisión | Elección | Razón |
|----------|----------|-------|
| Nivel de auto-registro | Una línea en `LOCAL_APPS` | Mínimo riesgo, Django-idiomático |
| Qué se auto-registra | URLs + middleware + settings | Cubre todos los pasos manuales actuales |
| Dónde vive la lógica | `config/plugins.py` | Testeable de forma aislada |
| Dónde declara la app | `AppConfig` (atributos de clase) | Punto de metadatos nativo de Django |

## Contrato del AppConfig

Cada app que quiera auto-registrarse añade atributos opcionales. Si el atributo no existe, no pasa nada.

```python
class MiAppConfig(AppConfig):
    name = "apps.mi_app"

    # Lista de dicts con prefix, urlconf, namespace (opcional)
    plugin_urls = [
        {"prefix": "admin/mi-app/", "urlconf": "apps.mi_app.urls", "namespace": None},
    ]

    # Lista de dicts con middleware y insert_after (opcional)
    plugin_middleware = [
        {
            "middleware": "apps.mi_app.middleware.MiMiddleware",
            "insert_after": "django.contrib.auth.middleware.AuthenticationMiddleware",
        }
    ]

    # Dict de settings a inyectar solo si no existen ya
    plugin_settings = {
        "MI_SETTING": os.getenv("MI_SETTING", "default"),
    }

    def ready(self):
        import apps.mi_app.signals  # noqa
```

### Reglas del contrato

- `plugin_urls`: cada entrada genera un `path(prefix, include(urlconf))` en `urlpatterns`.
- `plugin_middleware`: `insert_after` coloca el middleware inmediatamente después del middleware indicado. Si no se especifica, se hace `append`. Si ya está en la lista, se ignora.
- `plugin_settings`: solo se inyectan keys que no existan ya en `globals()` de `base.py` — nunca sobreescriben settings existentes.

## Arquitectura

```
config/
  plugins.py         ← motor de auto-registro (nuevo)
  settings/
    base.py          ← llama autoregister_plugins() al final (modificado)
  urls.py            ← usa _plugin_urls en lugar de paths hardcodeados (modificado)
  tests_plugins.py   ← tests del motor (nuevo)

apps/
  notifications/
    apps.py          ← añade plugin_urls (modificado)
  audit/
    apps.py          ← añade plugin_middleware (modificado)
  config/
    apps.py          ← sin cambios (no tiene URLs ni middleware extra)
  permissions/
    apps.py          ← sin cambios (no tiene URLs ni middleware extra)
```

## `config/plugins.py`

```python
from django.apps import apps as django_apps

def autoregister_plugins(installed_apps, middleware, settings_module):
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

## Integración en `base.py`

Al final del archivo, después de definir `MIDDLEWARE` e `INSTALLED_APPS`:

```python
from config.plugins import autoregister_plugins

_plugin_urls = autoregister_plugins(INSTALLED_APPS, MIDDLEWARE, globals())
```

## Integración en `config/urls.py`

Reemplazar el `path` hardcodeado de notifications:

```python
from config.settings.base import _plugin_urls

urlpatterns = [
    path("i18n/", include("django.conf.urls.i18n")),
    # ... resto de urls fijas ...
] + [
    path(u["prefix"], include(u["urlconf"]))
    for u in _plugin_urls
]
```

## Testing (`config/tests_plugins.py`)

| Test | Qué verifica |
|------|-------------|
| `test_urls_registered` | URLs de apps con `plugin_urls` aparecen en el resultado |
| `test_middleware_insert_after` | Middleware queda inmediatamente después del indicado |
| `test_middleware_no_duplicate` | Middleware ya presente no se duplica |
| `test_settings_not_overwrite` | Settings existentes no se sobreescriben |
| `test_app_without_attributes` | Apps sin atributos no lanzan error |

## Cómo agregar una nueva app como plugin

1. Copiar la carpeta en `apps/`
2. Añadir `"apps.mi_app"` en `LOCAL_APPS` en `config/settings/base.py`
3. Ejecutar `make migrate`

Eso es todo. URLs, middleware y settings se activan automáticamente si la app los declara en su `AppConfig`.

## Apps v2 actualizadas

| App | plugin_urls | plugin_middleware | plugin_settings |
|-----|-------------|-------------------|-----------------|
| notifications | ✅ `admin/notifications/` | — | `WEBHOOK_SECRET` |
| audit | — | ✅ después de `AuthenticationMiddleware` | — |
| config | — | — | — |
| permissions | — | — | — |
