# UX/UI Admin Upgrade — Smart Admin Template

**Fecha:** 2026-05-21
**Branch:** feature/v2
**Objetivo:** Mejorar la UX/UI genérica del template admin usando Unfold nativo + htmx + Chart.js, de forma que cada nuevo proyecto que use el template herede estas mejoras sin trabajo extra.

---

## Contexto

El template usa Django 6 + Unfold 0.40. Las apps opcionales (`notifications`, `audit`, `config`, `permissions`) ya existen pero sus admin no aprovechan todas las capacidades de Unfold. No hay dashboard de inicio, no hay notificaciones in-app visibles en el header, y no se usa htmx para interactividad.

## Decisiones de diseño

- **Sin WebSockets** — notificaciones in-app via polling htmx cada 30s (suficiente para un template base)
- **Dashboard con estructura, no métricas de negocio** — widgets de ejemplo con datos reales del sistema (usuarios, audit, notifications) que cada proyecto reemplaza
- **htmx + Chart.js CDN** — sin npm, sin build step, carga lazy de Chart.js solo en el dashboard
- **Unfold nativo máximo** — tabs, compressed_fields, warn_unsaved_change, actions con feedback

---

## Sección 1 — Dependencias y estructura base

### Nuevas dependencias

`requirements/base.txt`:
```
django-htmx>=1.17
```

### Frontend (CDN, sin build)

- **htmx** — CDN en `templates/admin/base_site.html` (disponible en todo el admin)
- **Chart.js** — CDN solo en `templates/admin/dashboard.html` (carga lazy)

### Archivos nuevos

```
templates/
  admin/
    base_site.html              ← override Unfold: htmx CDN + bell icon en header
    dashboard.html              ← página de inicio con grid de widgets
  partials/
    notifications_bell.html     ← bell icon + badge + dropdown
    notifications_list.html     ← lista de no leídas (respuesta htmx)
    dashboard_card.html         ← stat card reutilizable
    dashboard_chart.html        ← slot Chart.js con placeholder documentado

apps/
  core/
    dashboard.py                ← dashboard_callback(request, context)
  notifications/
    urls.py                     ← endpoints de notificaciones in-app
    views.py                    ← vistas htmx (unread-count, unread-list, mark-read)
```

### Cambios en settings

`config/settings/base.py`:
- Agregar `"django_htmx"` a `DJANGO_APPS`
- Agregar `"django_htmx.middleware.HtmxMiddleware"` a `MIDDLEWARE`
- Configurar `UNFOLD["DASHBOARD_CALLBACK"]` → `"apps.core.dashboard.dashboard_callback"`

`config/urls.py`:
- Incluir `apps.notifications.urls` bajo `/admin/notifications/`

---

## Sección 2 — Notificaciones in-app (bell icon)

### Flujo completo

1. Bell icon montado en el header del admin via `UNFOLD["EXTENSIONS"]["filters"]`
2. Badge con conteo de `Notification` con `channel="in_app"` y `read_at=None` del usuario actual
3. htmx polling cada 30s a `GET /admin/notifications/unread-count/` — actualiza solo el badge
4. Click en bell → htmx carga `GET /admin/notifications/unread-list/` → dropdown con últimas 10
5. Al abrir dropdown → `POST /admin/notifications/mark-read/` → marca todas `read_at=now()` → retorna badge actualizado (0)

### Endpoints nuevos

| Método | URL | Vista | Descripción |
|--------|-----|-------|-------------|
| GET | `/admin/notifications/unread-count/` | `unread_count_view` | Retorna partial del badge |
| GET | `/admin/notifications/unread-list/` | `unread_list_view` | Retorna partial con últimas 10 no leídas |
| POST | `/admin/notifications/mark-read/` | `mark_read_view` | Marca todas leídas, retorna badge actualizado |

Todas las vistas requieren `@login_required`. Solo responden a requests htmx (`request.htmx`).

### Templates htmx

`notifications_bell.html`:
```html
<span hx-get="/admin/notifications/unread-count/"
      hx-trigger="every 30s"
      hx-swap="outerHTML">
  <!-- badge con conteo -->
</span>
```

`notifications_list.html`: lista de cards con título, body truncado, timestamp relativo.

---

## Sección 3 — Dashboard de inicio

### Configuración Unfold

```python
# config/settings/base.py
UNFOLD = {
    ...
    "DASHBOARD_CALLBACK": "apps.core.dashboard.dashboard_callback",
}
```

### Layout

```
┌─────────────┬─────────────┬─────────────┐
│  Stat Card  │  Stat Card  │  Stat Card  │
│  Usuarios   │  No leídas  │  Audit hoy  │
├─────────────┴─────────────┴─────────────┤
│         Chart Slot (placeholder)         │
│      "Agrega tu gráfica aquí"           │
├─────────────┬───────────────────────────┤
│  Últimos 5  │      Últimas 5 entradas   │
│  usuarios   │      de auditoría         │
└─────────────┴───────────────────────────┘
```

### `apps/core/dashboard.py`

```python
def dashboard_callback(request, context):
    context.update({
        "stat_cards": [...],   # total usuarios, notif no leídas, audit hoy
        "recent_users": [...],
        "recent_audit": [...],
    })
    return context
```

Cada proyecto extiende o reemplaza esta función. El archivo incluye comentarios documentando cómo hacerlo.

### Chart slot

`dashboard_chart.html` incluye Chart.js con datos de ejemplo (array hardcodeado) y un comentario explícito:
```html
<!-- PROYECTO: reemplaza chartData con datos reales de tu app -->
```

---

## Sección 4 — Mejoras genéricas a ModelAdmin existentes

Todas son cambios de configuración en los admin actuales, sin código nuevo.

| Admin | Mejora |
|-------|--------|
| `AuditLogAdmin` | `tabs = True` en fieldsets, `show_full_result_count = False`, `warn_unsaved_change = True` |
| `NotificationAdmin` | `tabs = True`, bulk action "Marcar seleccionadas como leídas", `warn_unsaved_change = True` |
| `UserAdmin` | `compressed_fields = True`, `list_display_links` explícito, `warn_unsaved_change = True` |
| `WebhookEndpointAdmin` | `warn_unsaved_change = True`, `list_display_links` explícito |
| `SiteConfigAdmin` | `warn_unsaved_change = True` |
| `RoleAdmin` / `UserRoleAdmin` | `compressed_fields = True`, `warn_unsaved_change = True` |

### Bulk action en NotificationAdmin

```python
@action(description=_("Marcar seleccionadas como leídas"))
def mark_as_read(self, request, queryset):
    updated = queryset.filter(read_at__isnull=True).update(read_at=now())
    self.message_user(request, _(f"{updated} notificaciones marcadas como leídas."))
```

---

## Tests requeridos

- `tests/test_notifications_views.py` — unread_count, unread_list, mark_read (login required, htmx only)
- `tests/test_dashboard.py` — dashboard_callback retorna contexto esperado
- Actualizar `apps/notifications/tests.py` — cubrir la nueva bulk action

---

## Archivos modificados (resumen)

| Archivo | Tipo de cambio |
|---------|---------------|
| `requirements/base.txt` | Agregar django-htmx |
| `config/settings/base.py` | UNFOLD config, MIDDLEWARE, DJANGO_APPS |
| `config/urls.py` | Include notifications urls |
| `apps/core/dashboard.py` | Nuevo |
| `apps/notifications/urls.py` | Nuevo |
| `apps/notifications/views.py` | Nuevo |
| `apps/core/admin.py` | Mejoras Unfold |
| `apps/audit/admin.py` | Mejoras Unfold |
| `apps/notifications/admin.py` | Mejoras Unfold + bulk action |
| `apps/config/admin.py` | Mejoras Unfold |
| `apps/permissions/admin.py` | Mejoras Unfold |
| `templates/admin/base_site.html` | Nuevo |
| `templates/admin/dashboard.html` | Nuevo |
| `templates/partials/notifications_bell.html` | Nuevo |
| `templates/partials/notifications_list.html` | Nuevo |
| `templates/partials/dashboard_card.html` | Nuevo |
| `templates/partials/dashboard_chart.html` | Nuevo |
