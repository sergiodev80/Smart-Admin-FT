# Smart AdminAI Template — Contexto técnico

## Stack

| Capa | Tecnología |
|------|-----------|
| Framework | Django 6 + Python 3.12 |
| Admin UI | Unfold Admin (`unfold.admin.ModelAdmin`) |
| DB principal | PostgreSQL (modelos Django) |
| Contenedor | Docker (dev: `docker/Dockerfile.dev`) |
| Auth | Custom User model (`apps.core.User`) |
| i18n | Django i18n — idiomas: `es` (default), `en` |

## Estructura de apps

```
apps/
  core/          — Infraestructura: User model, auth, contexto Unfold (nunca opcional)
  config/        — Plugin core: settings dinámicos editables desde el admin
  permissions/   — Plugin core: roles y permisos granulares
  audit/         — Plugin core: registro de auditoría
  notifications/ — Plugin core: notificaciones in-app, email, webhook
  <nueva-app>/   — Plugin de dominio: específico del proyecto
```

### Clasificación de apps

| Tipo | Apps | Descripción |
|------|------|-------------|
| **Infraestructura** | `core` | Nunca opcional. Todo depende de ella. No es un plugin. |
| **Plugin core** | `config`, `permissions`, `audit`, `notifications` | Incluidas en el template, reutilizables en cualquier proyecto. Opcionales. |
| **Plugin de dominio** | cualquier app nueva | Específica del proyecto. Creada con el skill `/new-app`. |

**Regla:** Si quitar la app rompe otras apps → infraestructura. Si solo elimina funcionalidad propia → plugin.

### Responsabilidad de cada componente

- **core**: modelo `User` (sin roles hardcodeados), flujo de solicitud de acceso, contexto Unfold. Los roles se gestionan desde `apps.permissions` — cargar con `make loaddata`.

## Reglas que nunca se rompen

1. **Los modelos Django van en PostgreSQL.** Base de datos principal del proyecto.
2. **Tests obligatorios.** Toda nueva funcionalidad requiere tests antes de considerarse completa.
3. **Idioma del código.** Variables, funciones y comentarios en inglés. Textos de UI en español envueltos en `_()` o `{% trans %}`.
4. **Patrón Service para integraciones externas.** Todo acceso a sistemas externos (APIs, DBs externas, FTP) va en una clase `*Service` dentro de la app correspondiente, nunca directo desde vistas o admin.

## URLs base registradas

| Path | Nombre | Descripción |
|------|--------|-------------|
| `/admin/` | — | Unfold Admin |
| `/solicitar-acceso/` | `request_access` | Solicitud de acceso (unauthenticated) |
| `/i18n/` | — | Cambio de idioma |

## Patrón de vistas custom (fuera del admin)

Las vistas que usan el layout de Unfold deben agregar el contexto del admin:

```python
from django.contrib import admin

context.update(admin.site.each_context(request))
return render(request, "mi_template.html", context)
```

## Patrón Service para integraciones externas

```python
class MiServicioExterno:
    @staticmethod
    def get_algo(param):
        try:
            # conexión al sistema externo
            resultado = ...
            return resultado
        except Exception as e:
            logger.error("Error en MiServicioExterno: %s", e)
            return None
```

## Comandos frecuentes

```bash
make up              # Levantar entorno de desarrollo
make upd             # Levantar en background
make down            # Bajar contenedores
make migrate         # Correr migraciones
make makemigrations  # Crear migraciones
make test            # Correr tests
make messages        # Generar archivos de traducción
make compilemessages # Compilar traducciones
make createsuperuser # Crear superusuario
make shell           # Shell de Django
make logs            # Ver logs del servidor
```

## Variables de entorno requeridas

Copiar `.env.example` a `.env.dev` y completar:

```bash
cp .env.example .env.dev
```

Variables críticas:

- `SECRET_KEY`, `DEBUG=True`, `ALLOWED_HOSTS`
- `DB_*` — PostgreSQL (coincide con docker-compose.dev.yml)
- `EMAIL_*` — en dev usar `console.EmailBackend`

**Settings module:** En desarrollo no se define `DJANGO_SETTINGS_MODULE` — Django carga
`config/settings/base.py` directamente, que lee todo desde `.env.dev` vía `load_dotenv()`.

## Al iniciar un proyecto desde este template

1. Renombrar referencias `app_db_dev` en `docker-compose.dev.yml` al nombre del proyecto
2. Actualizar `SITE_TITLE` y `SITE_HEADER` en `config/settings/base.py`
3. Actualizar `DEFAULT_FROM_EMAIL` con el email real del proyecto
4. Agregar las apps específicas del proyecto en `LOCAL_APPS`
5. Crear las migraciones iniciales: `make makemigrations && make migrate`
6. Crear superusuario: `make createsuperuser`

## Diseño UI

Para cualquier tarea de UI (templates, vistas, admin) usar el skill `solid-platform-design`
que carga automáticamente las guías de componentes Unfold del proyecto.

---

## Plugin System

Toda app de dominio o plugin core se activa con una sola línea en `LOCAL_APPS`. URLs, middleware y settings propios se auto-registran desde el `AppConfig` de la app — sin tocar `config/urls.py` ni `MIDDLEWARE` manualmente.

### Contrato del AppConfig (toda app nueva debe declarar estos atributos)

```python
class MiAppConfig(AppConfig):
    name = "apps.mi_app"

    plugin_urls = [
        # URLs propias fuera del admin — se registran automáticamente antes de admin/
        {"prefix": "admin/mi-app/", "urlconf": "apps.mi_app.urls"},
    ]
    plugin_middleware = [
        # Middleware propio con orden explícito
        {"middleware": "apps.mi_app.middleware.MiMiddleware",
         "insert_after": "django.contrib.auth.middleware.AuthenticationMiddleware"},
    ]
    plugin_settings = {
        # Settings leídos de env vars, inyectados solo si no existen ya
        "MI_SETTING": os.getenv("MI_SETTING", "default"),
    }
```

Atributos vacíos (`[]`, `{}`) también deben declararse — son el contrato explícito de la app.

### Activar una app

1. Copiar la carpeta en `apps/`
2. Añadir `"apps.mi_app"` en `LOCAL_APPS` en `config/settings/base.py`
3. Ejecutar `make migrate`

## Apps v2 — Módulos opcionales

Activar cualquier app v2:
1. Descomentar la app en `LOCAL_APPS` en `config/settings/base.py`
2. Ejecutar `make migrate`

### apps/config — Configuración dinámica

Settings del sistema editables desde el admin sin tocar código (clave-valor con tipos).

```python
from apps.config.services import ConfigService

value = ConfigService.get("mi_clave", default="fallback")
ConfigService.set("mi_clave", "nuevo_valor")
```

### apps/audit — Registro de auditoría completo

Captura CRUD del admin, login, logout y navegación (opcional).

Agregar `AuditMixin` a cualquier `ModelAdmin` para auto-registrar CRUD:

```python
from apps.audit.mixins import AuditMixin
from unfold.admin import ModelAdmin

class MiModelAdmin(AuditMixin, ModelAdmin):
    ...
```

Para rastrear navegación, el `AuditMiddleware` se registra automáticamente vía el plugin system al activar la app.

### apps/notifications — Notificaciones (in-app + email + webhook)

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

Webhooks firmados con HMAC-SHA256 via `X-Signature` header.

### apps/permissions — Roles y permisos granulares

Cargar roles por defecto tras migrar:
```bash
docker compose -f docker-compose.dev.yml exec web_dev python manage.py loaddata apps/permissions/fixtures/default_roles.json
```

## Reglas transversales v2

- Todo `ModelAdmin` hereda de `unfold.admin.ModelAdmin`.
- Todo string de UI en `_()` o `{% trans %}` desde el primer commit.
- Traducciones centralizadas en `locale/es/` y `locale/en/` (raíz del proyecto).
- Lógica de negocio solo en clases `*Service`, nunca en vistas o admin.
- Si una funcionalidad requiere algo no disponible en Unfold nativo, consultar antes de implementar.
