---
name: solid-platform-design
description: Use when building any UI in solid_platform — tables, badges, forms, buttons, nav tabs, pages authenticated or unauthenticated. Triggers on any template, view, or admin task in the project.
---

# Solid Platform — Guías de Diseño Unfold

## Principio rector

**Primero buscar un componente nativo de Unfold. Si no existe, buscar en los componentes custom del proyecto. Si tampoco existe, preguntar antes de inventar.**
Nunca usar HTML/CSS manual cuando existe un componente equivalente (Unfold o custom).

```
¿Existe componente/helper Unfold para esto?
    SÍ → usarlo (ver catálogo completo abajo)
    NO → ¿existe componente custom del proyecto en templates/unfold/components/?
        SÍ → usarlo (ver catálogo de componentes custom abajo)
        NO → STOP: proponer 2-3 opciones al usuario antes de implementar
```

Documentación oficial: https://unfoldadmin.com/docs/
Demo oficial: https://demo.unfoldadmin.com/en/admin/

---

## COMPONENTES CUSTOM DEL PROYECTO

Ubicación: `templates/unfold/components/`
Invocación: `{% component "unfold/components/nombre.html" with param=valor %}{% endcomponent %}`
Requieren: `{% load i18n unfold %}` en el template que los usa.

Referencia completa: `docs/ui-components.md`

### Catálogo

| Componente | Archivo | Parámetros clave | Cuándo usarlo |
|------------|---------|-----------------|---------------|
| Toast | `toast.html` | *(ninguno — se registra una vez en base_site.html)* | Feedback de acciones HTMX. Activar desde Python: `response["HX-Trigger"] = json.dumps({"showToast": {"type": "success", "title": "...", "body": "..."}})` |
| Confirm Dialog | `confirm_dialog.html` | `title`, `body`, `confirm_label`, `cancel_label`, `danger`, `confirm_text`, `action_url`, `hx_delete` | Confirmación antes de acción destructiva. Modo simple (botones) o estricto (escribir texto) |
| Data List | `data_list.html` | `items` (list de dicts), `layout` (`horizontal`\|`grid`) | Mostrar campos etiqueta/valor de un objeto (detalle, ficha, modal) |
| Empty State | `empty_state.html` | `icon`, `title`, `subtitle`, `action_label`, `action_url`, `class` | Estado vacío de listas, tablas o paneles |
| Skeleton | `skeleton.html` | `type` (`lines`\|`table`), `rows`, `cols`, `avatar` | Placeholder de carga mientras HTMX espera respuesta |
| Page Header | `page_header.html` | `title`, `subtitle`, `breadcrumbs` (list), slot para acciones | Cabecera de página con título, subtítulo, breadcrumbs y botones de acción |
| Filter Tabs | `filter_tabs.html` | `tabs` (list con `label`, `url`, `active`, `count_url`, `badge_type`) | Tabs de filtro con contadores async (HTMX `hx-trigger="load"`) |
| Stat Card | `stat_card.html` | `title`, `value`, `icon`, `icon_color`, `trend`, `trend_label`, `href` | KPI card en dashboards. Trend: positivo/negativo/cero |
| Inline Edit | `inline_edit.html` | `value`, `field_name`, `patch_url`, `type` (`text`\|`select`\|`textarea`), `options` | Edición inline click-to-edit con HTMX PATCH |
| Modal Content | `modal_content.html` | `title`, `subtitle`, `icon`, `size` (`sm`\|`md`\|`lg`\|`xl`), `footer`, `close_label` | Shell para contenido de modales cargados con HTMX |
| Split Panel | `split_panel.html` | `detail_target`, `list_title`, `empty_icon`, `empty_title` | Layout master-detail 35/65. Lista izquierda, detalle HTMX derecho |
| Copy to Clipboard | `copy_to_clipboard.html` | `value`, `label`, `show_value`, `truncate` | Valor copiable con feedback ícono ✓ por 2 segundos (Alpine.js) |

### Reglas de uso

- **Toast vs Django messages:** HTMX action sin redirect → Toast. Formulario con redirect → `{% include "unfold/helpers/messages.html" %}`.
- **Inline Edit:** El endpoint debe recibir PATCH y retornar el componente completo con `outerHTML` swap para reinicializar Alpine.
- **Skeleton:** Usar con `hx-trigger="load"` en un contenedor HTMX — reemplazado por el contenido real.
- **Filter Tabs:** `count_url` debe retornar texto plano (solo el número, sin HTML).
- **Copy to Clipboard:** Requiere HTTPS o localhost (`navigator.clipboard` API).
- **Modal Content:** El partial de la vista no lleva `{% extends %}` — solo `{% load i18n unfold %}`.
- **Split Panel:** Reutiliza `empty_state.html` para el estado inicial del panel derecho.
- **Confirm Dialog — modo estricto:** Pasar `confirm_text="ELIMINAR"` para requerir que el usuario escriba ese texto antes de confirmar.

### Toast — activación desde Django

```python
import json
from django.http import HttpResponse

def mi_accion_htmx(request):
    # ... lógica ...
    response = HttpResponse()
    response["HX-Trigger"] = json.dumps({
        "showToast": {"type": "success", "title": "Guardado", "body": "Los cambios fueron guardados."}
    })
    return response
```

Tipos disponibles: `success`, `error`, `warning`, `info`.

### Data List — estructura de items

```python
context["items"] = [
    {"label": _("Nombre"), "value": obj.name, "type": "text"},
    {"label": _("Estado"), "value": obj.status, "type": "badge", "badge_type": "success"},
    {"label": _("Fecha"), "value": obj.created_at, "type": "date"},
    {"label": _("ID"), "value": obj.uuid, "type": "mono"},
    {"label": _("URL"), "value": "https://...", "type": "link", "link_label": _("Ver")},
]
```

### Filter Tabs — estructura en vista

```python
context["filter_tabs"] = [
    {"label": _("Todos"), "url": "?", "active": not request.GET.get("estado"),
     "count_url": "/api/counts/?estado=all", "badge_type": "neutral"},
    {"label": _("Activos"), "url": "?estado=active", "active": request.GET.get("estado") == "active",
     "count_url": "/api/counts/?estado=active", "badge_type": "success"},
]
```

### Stat Card — uso en dashboard

```python
context["stats"] = [
    {"title": _("Usuarios"), "value": "1,234", "icon": "group",
     "icon_color": "primary", "trend": 12, "trend_label": _("vs mes anterior")},
]
```

```django
{% for stat in stats %}
  {% component "unfold/components/stat_card.html" with title=stat.title value=stat.value icon=stat.icon icon_color=stat.icon_color trend=stat.trend trend_label=stat.trend_label %}
  {% endcomponent %}
{% endfor %}
```

---

## CATÁLOGO COMPLETO DE UNFOLD

### Componentes (`{% component "unfold/components/X" with ... %}{% endcomponent %}`)

| Componente | Ruta | Parámetros clave | Uso |
|------------|------|-----------------|-----|
| Card | `unfold/components/card.html` | `title`, `label`, `action`, `icon`, `footer`, `href`, `disable_border`, `class` | Contenedor con borde, ideal para KPIs y secciones |
| Table | `unfold/components/table.html` | `table` (dict con `headers`+`rows`), `striped`, `card_included`, `height` | Tabla de datos en dashboard |
| Button | `unfold/components/button.html` | `submit`, `href`, `variant` (`primary`\|`secondary`), `class` | Botones de acción |
| Progress | `unfold/components/progress.html` | `title`, `description`, `value`, `items` (multi-segmento) | Barras de progreso |
| Chart Bar | `unfold/components/chart/bar.html` | `data` (JSON), `height`, `options` | Gráfico de barras (Chart.js) |
| Chart Line | `unfold/components/chart/line.html` | `data` (JSON), `height`, `options` | Gráfico de línea (Chart.js) |
| Tracker | `unfold/components/tracker.html` | `data` | Tracker de actividad tipo GitHub |
| Cohort | `unfold/components/cohort.html` | `data` | Análisis de cohortes |
| Flex | `unfold/components/flex.html` | `class`, `col` | Layout flexible |
| Container | `unfold/components/container.html` | `class` | Wrapper con max-width |
| Separator | `unfold/components/separator.html` | `class` | Divisor horizontal |
| Title | `unfold/components/title.html` | `class` | Título/heading |
| Text | `unfold/components/text.html` | `class` | Párrafo de texto |
| Navigation | `unfold/components/navigation.html` | `class`, `items` | Lista de links de navegación |

### Helpers (`{% include "unfold/helpers/X" with ... %}`)

| Helper | Ruta | Uso |
|--------|------|-----|
| Label/Badge | `unfold/helpers/label.html` | Badges de estado con color semántico |
| Field | `unfold/helpers/field.html` | Campo de formulario con estilos Unfold |
| Messages | `unfold/helpers/messages.html` | Flash messages del sistema |
| Error note | `unfold/helpers/messages/errornote.html` | Bloque de errores de formulario |
| Error inline | `unfold/helpers/messages/error.html` | Error individual |
| Page title (unauth) | `unfold/helpers/unauthenticated_title.html` | Título en páginas sin login |

---

## 1. Layouts

| Situación | Layout |
|-----------|--------|
| Página dentro del admin (autenticado) | `{% extends "unfold/layouts/base.html" %}` |
| Login, registro, páginas públicas | `{% extends "unfold/layouts/unauthenticated.html" %}` |

**Siempre** cargar `{% load i18n unfold %}`. Sin `unfold` no funcionan `{% component %}` ni helpers.

Vistas custom autenticadas necesitan contexto del admin:
```python
context.update(admin.site.each_context(request))
```

---

## 2. Badges / Labels

**Nunca** usar `<span>` con clases Tailwind manuales para estados.
Docs: https://unfoldadmin.com/docs/decorators/display/

```django
{% component "unfold/helpers/label.html" with text=valor type=variante %}
{% endcomponent %}
```

| Parámetro | Valores |
|-----------|---------|
| `text` | string visible |
| `type` | `success` · `warning` · `info` · `danger` · `primary` |
| `size` | `md` (default) |
| `icon` | nombre Material Symbol |
| `href` | URL — convierte el badge en enlace |

| Estado del negocio | `type` |
|-------------------|--------|
| Activo, aprobado, disponible | `success` |
| En revisión, pendiente | `warning` |
| Informativo, neutro, nuevo | `info` |
| Rechazado, cancelado, error | `danger` |

### En ModelAdmin — `@display` con label

```python
from unfold.decorators import display  # NO django.contrib.admin.decorators

@display(
    description=_("Status"),
    ordering="status",
    label={"active": "success", "pending": "warning", "inactive": "danger"},
)
def show_status(self, obj):
    return obj.status
```

`@display` también soporta:
- `header=True` → celda con dos líneas + badge circular: `return ["Título", "Subtítulo", "AB", {"path": "img.jpg"}]`
- `dropdown=True` → menú desplegable: `return {"title": "...", "items": [{"title": "...", "link": "..."}]}`

---

## 3. Tablas en vistas custom

Para tablas en dashboard usar el componente `unfold/components/table.html`:

```python
# Vista Python
context["tabla"] = {
    "headers": [_("Col 1"), _("Col 2")],
    "rows": [["valor a", "valor b"]],
}
```

```django
{% component "unfold/components/card.html" with title=_("Mi tabla") %}
    {% component "unfold/components/table.html" with table=tabla card_included=1 striped=1 %}
    {% endcomponent %}
{% endcomponent %}
```

Para tablas en vistas custom con badges por celda (patrón `translations/job_list.html`):

```django
<div class="rounded-default overflow-hidden border border-base-200 dark:border-base-800 bg-white dark:bg-base-900">
    <table class="w-full text-sm">
        <thead>
            <tr class="border-b border-base-200 dark:border-base-800 bg-base-50 dark:bg-base-800/50">
                <th class="px-4 py-3 text-left text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">Header</th>
            </tr>
        </thead>
        <tbody class="divide-y divide-base-200 dark:divide-base-800">
            <tr class="hover:bg-base-50 dark:hover:bg-base-800/30 transition-colors">
                <td class="px-4 py-3 text-gray-900 dark:text-gray-100">valor</td>
            </tr>
        </tbody>
    </table>
</div>
```

| Tipo de celda | Clases |
|---------------|--------|
| Texto principal | `text-gray-900 dark:text-gray-100` |
| Texto secundario | `text-gray-500 dark:text-gray-400` |
| IDs / código | `font-mono text-xs text-gray-700 dark:text-gray-300` |
| Centrado | `text-center` |
| Truncado | `max-w-xs truncate` |

Valor vacío: usar `—` (em dash). Estado vacío — usar el componente custom:
```django
{% component "unfold/components/empty_state.html"
   with icon="search_off" title=_("Sin resultados") subtitle=_("No se encontraron registros.") %}
{% endcomponent %}
```

---

## 4. Filtros en ModelAdmin

Requiere `"unfold.contrib.filters"` en `INSTALLED_APPS`.
Docs: https://unfoldadmin.com/docs/filters/introduction/

```python
from unfold.contrib.filters.admin import (
    FieldTextFilter, TextFilter,           # texto
    RangeDateFilter, RangeDateTimeFilter,  # fechas
    ChoicesDropdownFilter,                 # choices del modelo
    RelatedDropdownFilter,                 # FK
    MultipleRelatedDropdownFilter,         # FK múltiple
)

class MiAdmin(ModelAdmin):
    list_filter_submit = True  # botón "Filtrar" (requerido para inputs)
    list_filter = [
        ("nombre", FieldTextFilter),
        ("fecha", RangeDateFilter),
        ("estado", ChoicesDropdownFilter),
        ("categoria", RelatedDropdownFilter),
    ]
```

---

## 5. Acciones

Docs: https://unfoldadmin.com/docs/actions/introduction/

```python
from unfold.decorators import action
from unfold.enums import ActionVariant

@action(
    description=_("Mi acción"),
    icon="check_circle",
    variant=ActionVariant.SUCCESS,  # DEFAULT · PRIMARY · SUCCESS · INFO · WARNING · DANGER
)
def mi_accion(self, request, queryset):
    ...
```

| Tipo | Atributo ModelAdmin | Ubicación visual |
|------|-------------------|-----------------|
| Global | `actions_list` | Sobre la tabla |
| Por fila | `actions_row` | Columna en cada fila |
| Detalle | `actions_detail` | Parte superior del form |
| Submit line | `actions_submit_line` | Junto al botón Guardar |

---

## 6. Tabs

Docs: https://unfoldadmin.com/docs/tabs/changelist/

**Changelist tabs** (entre modelos) — en `settings.py`:
```python
UNFOLD = {
    "TABS": [
        {
            "models": ["app.modelname"],
            "items": [
                {"title": _("Tab 1"), "link": reverse_lazy("admin:app_model_changelist")},
            ],
        },
    ],
}
```

**Changeform / fieldset tabs** — en el ModelAdmin directamente (ver docs).

---

## 7. Dashboard personalizado

Docs: https://unfoldadmin.com/docs/configuration/dashboard/

Crear `templates/admin/index.html`:
```django
{% extends "admin/base.html" %}
{% load i18n unfold %}

{% block content %}
    {% component "unfold/components/card.html" with title=_("KPI") %}
        {% component "unfold/components/progress.html" with title=_("Avance") value=75 description="75%" %}
        {% endcomponent %}
    {% endcomponent %}
{% endblock %}
```

Callback para contexto dinámico en `settings.py`:
```python
UNFOLD = {"DASHBOARD_CALLBACK": "apps.core.views.dashboard_callback"}
```
```python
def dashboard_callback(request, context):
    context.update({"mi_dato": calcular()})
    return context
```

---

## 8. Páginas custom dentro del admin

Docs: https://unfoldadmin.com/docs/configuration/custom-pages/

```python
from unfold.views import UnfoldModelAdminViewMixin
from django.views.generic import TemplateView

class MiVista(UnfoldModelAdminViewMixin, TemplateView):
    title = "Mi Página"
    permission_required = ()
    template_name = "mi_app/mi_template.html"

@admin.register(MiModelo)
class MiAdmin(ModelAdmin):
    def get_urls(self):
        return super().get_urls() + [
            path("mi-url/", self.admin_site.admin_view(
                MiVista.as_view(model_admin=self)
            ), name="mi_nombre"),
        ]
```

---

## 9. Modales / Dialogs

Unfold incluye un modal nativo en `unfold/helpers/modal.html` — se renderiza en el `<body>` de cada página automáticamente. Usa `openModal` en el `x-data` del body y el `id="modal-content"` como target.

### Patrón establecido — HTMX + modal nativo de Unfold

**Vista Django** — retorna un partial HTML (sin `extends`):
```python
@login_required
def mi_modal_view(request, pk):
    obj = get_object_or_404(MiModelo, pk=pk)
    return render(request, "mi_app/mi_modal.html", {"obj": obj})
```

**URL:**
```python
path("modal/<int:pk>/", mi_modal_view, name="mi_modal"),
```

**Template principal** — trigger + script en `{% block extrahead %}`:
```django
{% block extrahead %}
{{ block.super }}
<script>
    document.addEventListener("htmx:afterSwap", (e) => {
        if (e.detail.target.id === "modal-content") {
            Alpine.$data(document.body).openModal = true;
        }
    });
</script>
{% endblock %}

{# Botón trigger en la tabla #}
<button
    hx-get="{% url 'app:mi_modal' obj.pk %}"
    hx-target="#modal-content"
    hx-swap="innerHTML"
>
    <span class="material-symbols-outlined">open_in_new</span>
</button>
```

**Template del modal** (`mi_modal.html`) — usar el componente custom `modal_content.html`:
```django
{% load i18n unfold %}

{% component "unfold/components/modal_content.html" with title=obj.nombre size="md" %}
    {# Contenido del modal aquí #}
    {% component "unfold/components/data_list.html" with items=items %}{% endcomponent %}
{% endcomponent %}
```

Parámetros de `modal_content.html`: `title`, `subtitle`, `icon`, `size` (sm/md/lg/xl, default md), `footer` (HTML), `close_label`.

### Loading indicator en el trigger

Mientras HTMX espera la respuesta, mostrar spinner y ocultar el ícono normal.

**CSS en `{% block extrahead %}`:**
```django
{% block extrahead %}
{{ block.super }}
<style>
    .htmx-request .htmx-hide-on-request { display: none; }
    .htmx-request .htmx-show-on-request { display: inline !important; }
</style>
{% endblock %}
```

**Botón con `hx-indicator="this"`:**
```django
<button
    hx-get="{% url 'app:mi_modal' obj.pk %}"
    hx-target="#modal-content"
    hx-swap="innerHTML"
    hx-indicator="this"
>
    {# visible en reposo, oculto durante el request #}
    <span class="material-symbols-outlined htmx-hide-on-request">open_in_new</span>
    {# oculto en reposo, visible+girando durante el request #}
    <span class="material-symbols-outlined animate-spin htmx-show-on-request" style="display:none">progress_activity</span>
</button>
```

HTMX agrega `htmx-request` al elemento con `hx-indicator="this"` automáticamente durante el request y la elimina al terminar.

### Claves del patrón
- `Alpine.$data(document.body).openModal = true` — API correcta de Alpine v3 para acceder al state del body
- El script va en `{% block extrahead %}` con `{{ block.super }}` — es el único block de scripts disponible en Unfold
- El partial no lleva `{% extends %}` ni `{% load %}` innecesarios — solo `{% load i18n unfold %}`
- El cierre usa `x-on:click="openModal = false"` — Alpine ya maneja ESC y click fuera del panel

### Para acciones del admin (dialog de confirmación)
```python
@action(
    description=_("Aprobar"),
    dialog={
        "title": "Confirmar aprobación",
        "description": "¿Estás seguro?",
        "submit_text": _("Confirmar"),
        "form_class": MiForm,  # opcional, hereda de BaseDialogForm
    },
)
def aprobar(self, request, form):
    return HttpResponse(headers={"HX-Redirect": reverse_lazy(...)})
```
Docs: https://unfoldadmin.com/docs/actions/dialog-actions/

---

## 10. Inlines

```python
from unfold.admin import StackedInline, TabularInline  # NO los de django.contrib.admin
```

Tipos disponibles: StackedInline, TabularInline, NonrelatedInline, SortableInline, PaginatedInline, NestedInline.
Docs: https://unfoldadmin.com/docs/inlines/introduction/

---

## 10. ModelAdmin — opciones clave

```python
from unfold.admin import ModelAdmin

class MiAdmin(ModelAdmin):
    # Layout
    list_fullwidth = True          # tabla sin límite de ancho
    list_filter_sheet = True       # filtros en panel lateral (default)
    list_filter_submit = True      # botón "Filtrar" en panel
    compressed_fields = True       # campos compactos en changeform
    warn_unsaved_form = True       # alerta si sale sin guardar

    # Templates adicionales en changeform
    change_form_before_template = "mi_app/extra_before.html"
    change_form_after_template  = "mi_app/extra_after.html"

    # Acciones
    actions_list = [mi_accion_global]
    actions_row  = [mi_accion_fila]
```

Sidebar — agregar ítem en `config/settings/base.py`:
```python
UNFOLD["SIDEBAR"]["navigation"] += [{
    "title": "Mi Sección",
    "icon": "nombre_material_symbol",
    "items": [{"title": "Mi Vista", "icon": "icono", "link": "/mi-url/"}],
}]
```

---

## 11. Botones

```django
{# Primario #}
{% component "unfold/components/button.html" with submit=1 variant="primary" class="w-full" %}
    {% trans "Guardar" %} <span class="material-symbols-outlined text-sm">arrow_forward</span>
{% endcomponent %}

{# Secundario / link #}
{% component "unfold/components/button.html" with href=url variant="secondary" %}
    {% trans "Cancelar" %}
{% endcomponent %}
```

---

## 12. Formularios

```django
{# Campo con estilos Unfold #}
{% include "unfold/helpers/field.html" with field=form.campo %}

{# Mensajes de error #}
{% include "unfold/helpers/messages.html" %}
{% include "unfold/helpers/messages/errornote.html" with errors=form.errors %}
```

---

## 13. Íconos

Solo **Material Symbols** — ya incluidos en Unfold.
Búsqueda: https://fonts.google.com/icons

```django
<span class="material-symbols-outlined text-sm">nombre_icono</span>
```

Nunca agregar Font Awesome u otras librerías.

---

## 14. Internacionalización

Todo texto visible al usuario en `{% trans %}` / `_()`. Idiomas: `es` (default), `en`.

---

## 15. Filter Tabs en vistas custom

Usar el componente custom `filter_tabs.html` — incluye contadores async via HTMX:

```django
{% component "unfold/components/filter_tabs.html" with tabs=filter_tabs %}{% endcomponent %}
```

Estructura de `filter_tabs` en la vista Python:
```python
context["filter_tabs"] = [
    {"label": _("Todos"), "url": "?", "active": not request.GET.get("estado"),
     "count_url": reverse("mi_app:count") + "?estado=all", "badge_type": "neutral"},
    {"label": _("Activos"), "url": "?estado=active", "active": request.GET.get("estado") == "active",
     "count_url": reverse("mi_app:count") + "?estado=active", "badge_type": "success"},
]
```

El endpoint `count_url` debe retornar texto plano (solo el número). Si no hay contadores, omitir `count_url`.

Badge types disponibles: `success`, `warning`, `danger`, `info`, `neutral` (default).
