---
name: init-project
description: Use when a developer has just cloned the Smart Admin FT template and needs to configure it for a new project. Triggers on phrases like "inicializar proyecto", "configurar template", "init project", "setup proyecto", "empezar proyecto nuevo", "configurar proyecto". Runs a guided interview and applies all changes automatically — no manual file editing needed.
---

# init-project — Configuración inicial del template

## Objetivo

Guiar al dev en la configuración del template recién clonado mediante preguntas cortas y aplicar todos los cambios automáticamente. El dev no debe tocar archivos manualmente.

## Archivos que se modifican

| Archivo | Qué cambia |
|---------|-----------|
| `config/settings/base.py` | `SITE_TITLE`, `SITE_HEADER`, `DEFAULT_FROM_EMAIL`, `TIME_ZONE` |
| `docker-compose.dev.yml` | `container_name`, `POSTGRES_DB`, `DB_NAME` (prefijo del proyecto) |
| `.env.example` | `DEFAULT_FROM_EMAIL` |
| `CLAUDE.md` | Título del proyecto en el encabezado |

## Proceso

### Paso 1 — Entrevista (una pregunta a la vez)

Hacer estas preguntas en orden, una por mensaje:

**1. Nombre del proyecto**
> "¿Cómo se llama el proyecto? (ej: 'Gestión de Inventario' — se usará en el título del admin)"

**2. Slug del proyecto**
> "¿Qué slug corto usamos para los contenedores Docker y la base de datos? (solo letras minúsculas y guiones bajos, ej: `inventario` o `gestion_inv`)"
>
> Regla: máximo 20 caracteres, sin espacios, solo `[a-z0-9_]`.

**3. Email del proyecto**
> "¿Cuál es el email remitente del proyecto? (ej: `noreply@miempresa.com`)"

**4. Zona horaria**
> "¿Qué zona horaria usa el proyecto?"
> Opciones comunes:
> - A) `America/Bogota` (Colombia, Ecuador, Perú)
> - B) `America/Mexico_City` (México)
> - C) `America/Santiago` (Chile)
> - D) `America/Argentina/Buenos_Aires` (Argentina)
> - E) `America/Caracas` (Venezuela)
> - F) `UTC` (mantener UTC)
> - O escribe otra zona válida de la lista de pytz

**5. Puerto local**
> "¿En qué puerto local correrá el admin en dev? (default: `8002`)"
> Útil si hay varios proyectos corriendo en paralelo.

---

### Paso 2 — Resumen antes de aplicar

Mostrar el resumen de cambios y pedir confirmación:

```
Voy a aplicar estos cambios:

- SITE_TITLE / SITE_HEADER → "<nombre>"
- DEFAULT_FROM_EMAIL → "<email>"
- TIME_ZONE → "<zona>"
- DB y contenedores → prefijo "<slug>" (ej: <slug>_db_dev, <slug>_web_dev)
- Puerto local → <puerto>
- CLAUDE.md → título actualizado

¿Aplicamos? (sí/no)
```

Solo proceder si el usuario confirma.

---

### Paso 3 — Aplicar cambios

Aplicar en este orden exacto:

#### `config/settings/base.py`

Reemplazar:
```python
"SITE_TITLE": "TODO: Nombre del proyecto",
"SITE_HEADER": "TODO: Nombre del proyecto",
```
Por:
```python
"SITE_TITLE": "<nombre>",
"SITE_HEADER": "<nombre>",
```

Reemplazar `TIME_ZONE`:
```python
TIME_ZONE = "UTC"
```
Por:
```python
TIME_ZONE = "<zona>"
```

Reemplazar el default de `DEFAULT_FROM_EMAIL` (solo si el usuario no configuró `EMAIL_*` en el env):
```python
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "noreply@example.com")
```
Por:
```python
DEFAULT_FROM_EMAIL = os.getenv("DEFAULT_FROM_EMAIL", "<email>")
```

#### `docker-compose.dev.yml`

Reemplazar todas las ocurrencias de `app_db_dev` por `<slug>_db_dev`.
Reemplazar `app_web_dev` por `<slug>_web_dev`.
Reemplazar el puerto `"8002:8000"` por `"<puerto>:8000"`.

#### `.env.example`

Reemplazar:
```
DEFAULT_FROM_EMAIL=noreply@example.com
```
Por:
```
DEFAULT_FROM_EMAIL=<email>
```

#### `CLAUDE.md`

Reemplazar la primera línea:
```markdown
# Smart AdminAI Template — Contexto técnico
```
Por:
```markdown
# <nombre> — Contexto técnico
```

---

### Paso 4 — Pasos manuales restantes

Después de aplicar los cambios, indicar al dev los pasos que no se pueden automatizar:

```
✅ Configuración aplicada. Pasos manuales que quedan:

1. Copiar el archivo de entorno:
   cp .env.example .env.dev

2. Editar .env.dev y completar:
   - SECRET_KEY (generar con: python -c "import secrets; print(secrets.token_urlsafe(50))")
   - DB_PASSWORD (cualquier string seguro)
   - EMAIL_* (si necesitas envío real de emails)

3. Levantar el entorno:
   make up

4. Correr migraciones:
   make migrate

5. Crear superusuario:
   make createsuperuser

6. Si usas apps/permissions, cargar roles por defecto:
   docker compose -f docker-compose.dev.yml exec web_dev python manage.py loaddata apps/permissions/fixtures/default_roles.json

7. Abrir el admin en: http://localhost:<puerto>/admin/
```

---

## Reglas de aplicación

- **Leer cada archivo antes de editarlo** — usar Read tool antes de cualquier Edit.
- **No modificar nada que el usuario no haya confirmado.**
- **Slug válido:** si el usuario ingresa caracteres inválidos, corregir automáticamente (espacios → `_`, mayúsculas → minúsculas) y mostrar el slug corregido antes de aplicar.
- **Puerto:** si el usuario acepta el default, usar `8002`.
- **Zona horaria:** si el usuario elige opción de letra (A-F), mapear al valor correcto antes de aplicar.
- **Commit al final:** después de aplicar todos los cambios, hacer un commit:
  ```bash
  git add config/settings/base.py docker-compose.dev.yml .env.example CLAUDE.md
  git commit -m "chore: init project — <nombre>"
  ```
