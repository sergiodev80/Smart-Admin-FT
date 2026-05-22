# Spec: Página de Notificaciones — Diseño moderno C3

**Fecha:** 2026-05-22  
**Estado:** Aprobado

---

## Resumen

Reemplazar la tabla Django/Unfold por defecto de `Notification` con una vista custom de lista + panel de detalle estilo C3, integrada en el admin de Unfold sin inventar componentes nuevos. en el caso que se necesite debe ser reutilizable por lo que necesi

---

## Modelo — Cambios

### Campo nuevo: `archived_at`

```python
archived_at = models.DateTimeField(null=True, blank=True, verbose_name=_("archivada el"))
```

- `archived_at=None` → notificación activa (aparece en "Todas" y "No leídas" si aplica)
- `archived_at` con valor → archivada (solo aparece en tab "Archivadas", excluida de "Todas")
- Archivar y marcar como leída son acciones independientes

Requiere migración.

---

## Vista custom — `NotificationListView`

Reemplaza el changelist de Unfold para `Notification`. Es una vista Django estándar decorada con `@staff_member_required`, registrada vía el sistema de plugins (`plugin_urls`), que inyecta el contexto de Unfold con `admin.site.each_context(request)`.

**No se toca `config/urls.py`.**

### URL

```
/admin/notifications/bandeja/
```

Registrada en `plugin_urls` del `NotificationsConfig`.

### Lógica de tabs

| Tab | Queryset |
|-----|----------|
| Todas | `archived_at__isnull=True` (no archivadas) |
| No leídas | `archived_at__isnull=True, read_at__isnull=True` |
| Archivadas | `archived_at__isnull=False` |

Filtro por `recipient=request.user`, `channel=IN_APP`.

### Panel de detalle

- Seleccionar un item de la lista carga el detalle vía HTMX (`hx-get`, `hx-target`, `hx-swap="innerHTML"`)
- El detalle se sirve desde una vista separada `NotificationDetailView` en `/admin/notifications/bandeja/<pk>/`

---

## Acciones (vistas HTMX)

Todas requieren `HX-Request` y `@staff_member_required`. Devuelven respuestas parciales.

| Acción | Método | URL | Efecto |
|--------|--------|-----|--------|
| Marcar como leída | POST | `/admin/notifications/bandeja/<pk>/mark-read/` | Setea `read_at=now()` |
| Archivar | POST | `/admin/notifications/bandeja/<pk>/archive/` | Setea `archived_at=now()` |
| Marcar todas leídas | POST | `/admin/notifications/bandeja/mark-all-read/` | Setea `read_at=now()` en todas las del tab activo |

Tras cada acción HTMX se refresca la lista y el panel via `HX-Trigger` response header.

---

## Botón "Ver sección relacionada"

- Solo visible si `notification.payload.get("url")` tiene valor
- Renderiza como `<a href="{{ url }}" target="_blank">` con ícono `open_in_new`
- Sin migración — usa el campo `payload` (JSONField) ya existente

---

## Templates

Todos dentro de `apps/notifications/templates/notifications/`:

| Archivo | Descripción |
|---------|-------------|
| `bandeja.html` | Página completa — extiende `admin/base.html` de Unfold |
| `partials/notif_list.html` | Lista izquierda (HTMX swap target) |
| `partials/notif_detail.html` | Panel derecho (HTMX swap target) |
| `partials/notif_detail_empty.html` | Estado vacío del panel |

### Diseño visual

- **Íconos:** `material-symbols-outlined` — misma fuente que Unfold, sin SVG inline
- **Colores:** variables CSS de Unfold (`text-important`, `text-subtle`, `bg-base-*`, `border-base-*`, `text-primary-*`)
- **No** se inventan colores hardcodeados
- Layout: lista fija 320px izquierda + panel flexible derecha, altura calculada para llenar la pantalla
- Agrupación por fecha: Hoy / Ayer / Esta semana / Anteriores
- Item no leído: borde izquierdo primario + punto indicador + texto bold
- Item leído: sin borde, texto sutil

### Íconos por canal/tipo

| Contexto | Ícono |
|----------|-------|
| In-app | `notifications` |
| Email | `mail` |
| Webhook | `webhook` |
| Marcar leída | `check_circle` |
| Archivar | `archive` |
| Ver relacionada | `open_in_new` |
| Marcar todas | `done_all` |

---

## Admin registration

El `ModelAdmin` de `Notification` en `admin.py` se mantiene para que el superadmin pueda gestionar notificaciones de otros usuarios vía la URL estándar `/admin/notifications/notification/`. La nueva vista custom es adicional, no reemplaza el admin existente.

Se agrega un link en el sidebar de Unfold apuntando a `/admin/notifications/bandeja/` vía la configuración `UNFOLD["SIDEBAR"]` en `settings/base.py`.

---

## Tests

- `test_bandeja_requires_login` — redirect si no autenticado
- `test_bandeja_tabs_filter` — cada tab devuelve el queryset correcto
- `test_mark_read_action` — setea `read_at`, requiere HTMX header
- `test_archive_action` — setea `archived_at`, excluye de tab "Todas"
- `test_payload_url_visible` — botón "Ver relacionada" aparece solo con `payload.url`
- `test_payload_url_hidden` — botón oculto sin `payload.url`

---

## Lo que NO se hace

- No se toca `config/urls.py`
- No se usan SVG inline ni emojis
- No se hardcodean colores (usar clases de Unfold/Tailwind existentes)
- No se crea un ModelAdmin nuevo (se reutiliza el existente)
- No se implementan tabs In-app/Email (quedan para iteración futura)
- No se implementa paginación (la lista carga las últimas 50 por ahora)
