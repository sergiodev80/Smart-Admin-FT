# Smart AdminAI Template v2

Template base para proyectos de administración interna con Django + Unfold Admin + Docker. Incluye sistema de plugins, módulos opcionales listos para activar y skills de Claude Code para scaffolding guiado.

## Stack

| Capa | Tecnología |
|------|-----------|
| Framework | Django 6 + Python 3.12 |
| Admin UI | Unfold Admin |
| Base de datos | PostgreSQL 16 |
| Contenedor | Docker (dev) |
| i18n | Español (default) + Inglés |

## Módulos incluidos

### Infraestructura (siempre activa)
- **core** — User model personalizado, roles, solicitud de acceso, login por email o username

### Plugins opcionales (activar con una línea en `LOCAL_APPS`)
| Plugin | Qué hace |
|--------|---------|
| `notifications` | Notificaciones in-app, email y webhook con firma HMAC |
| `audit` | Registro completo de CRUD, login, logout y navegación |
| `config` | Settings del sistema editables desde el admin sin tocar código |
| `permissions` | Roles y permisos granulares por objeto |
| `erp_sync` | Ejemplo de patrón Service para integraciones con sistemas externos |

## Inicio rápido

```bash
# 1. Clonar
git clone <repo-url> mi-proyecto
cd mi-proyecto

# 2. Configurar el proyecto (guiado por Claude)
# Abrir Claude Code y ejecutar:
# /init-project

# O manualmente:
cp .env.example .env.dev
# Editar .env.dev con los valores del proyecto

# 3. Levantar
make up

# 4. Migraciones y superusuario
make migrate
make createsuperuser
```

El admin corre en [http://localhost:8002/admin/](http://localhost:8002/admin/)

## Plugin system

Toda app nueva se activa con una línea en `LOCAL_APPS`. URLs, middleware y settings se auto-registran desde el `AppConfig` de la app — sin tocar `config/urls.py` ni `MIDDLEWARE`.

```python
# LOCAL_APPS en config/settings/base.py
LOCAL_APPS = [
    "apps.core",
    "apps.notifications",  # activar descomentando
    "apps.audit",
    "apps.config",
    "apps.permissions",
    # "apps.mi_nueva_app",  # agregar aquí
]
```

Cada app declara su propio contrato en `AppConfig`:

```python
class MiAppConfig(AppConfig):
    plugin_urls = [{"prefix": "admin/mi-app/", "urlconf": "apps.mi_app.urls"}]
    plugin_middleware = [{"middleware": "...", "insert_after": "..."}]
    plugin_settings = {"MI_SETTING": os.getenv("MI_SETTING", "")}
```

## Skills de Claude Code

| Skill | Cuándo usarlo |
|-------|--------------|
| `/init-project` | Al clonar el template — configura nombre, email, zona horaria, DB |
| `/new-app` | Para crear una nueva app de dominio con scaffolding guiado |
| `/solid-platform-design` | Para cualquier tarea de UI en templates o admin |

## Comandos frecuentes

```bash
make up              # Levantar entorno
make down            # Bajar contenedores
make migrate         # Correr migraciones
make test            # Correr tests
make shell           # Shell de Django
make logs            # Ver logs
make createsuperuser # Crear superusuario
make messages        # Generar traducciones
make compilemessages # Compilar traducciones
```
