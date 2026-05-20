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
  core/          — User model, acceso al sistema, solicitud de acceso
  <nueva-app>/   — Agregar apps específicas del proyecto aquí
```

### Responsabilidad de cada componente

- **core**: modelo `User` con roles (`admin`, `pm`, `translator`, `reviewer`), flujo de solicitud de acceso, contexto Unfold. Extender roles según necesidad del proyecto.

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
