---
name: solid-platform-design
description: Use when building any UI in solid_platform — tables, badges, forms, buttons, nav tabs, pages authenticated or unauthenticated. Triggers on any template, view, or admin task in the project.
---

# Solid Platform — Guías de Diseño Unfold

## Principio rector

**Primero buscar un componente nativo de Unfold. Si no existe, preguntar antes de inventar.**
Nunca usar HTML/CSS manual cuando existe un componente Unfold equivalente.

```
¿Existe componente/helper Unfold para esto?
    SÍ → usarlo (ver catálogo completo abajo)
    NO → ¿existe patrón ya usado en este proyecto?
        SÍ → seguirlo
        NO → STOP: proponer 2-3 opciones al usuario antes de implementar
```

Documentación oficial: https://unfoldadmin.com/docs/
Demo oficial: https://demo.unfoldadmin.com/en/admin/

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

Valor vacío: usar `—` (em dash). Estado vacío:
```django
<div class="border border-base-200 dark:border-base-800 rounded-default p-8 text-center bg-white dark:bg-base-900">
    <p class="text-gray-500 dark:text-gray-400">{% trans "No se encontraron registros." %}</p>
</div>
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

**Template del modal** (`mi_modal.html`) — partial sin `extends`, botón cerrar con `x-on:click="openModal = false"`:
```django
{% load i18n unfold %}

<div class="bg-white dark:bg-base-900 rounded-default p-6">
    {# Header #}
    <div class="flex items-start justify-between mb-6 pb-4 border-b border-base-200 dark:border-base-700">
        <h2 class="text-xl font-bold text-gray-900 dark:text-white">{{ obj }}</h2>
        <button type="button" x-on:click="openModal = false"
                class="p-1.5 rounded-default text-gray-400 hover:bg-base-100 dark:hover:bg-base-800 transition-colors">
            <span class="material-symbols-outlined text-xl leading-none">close</span>
        </button>
    </div>

    {# Contenido #}
    ...

    {# Footer #}
    <div class="pt-4 border-t border-base-200 dark:border-base-700 flex justify-end">
        <button type="button" x-on:click="openModal = false"
                class="px-4 py-2 text-sm font-medium rounded-default text-gray-600 dark:text-gray-300 hover:bg-base-100 dark:hover:bg-base-800 transition-colors">
            {% trans "Close" %}
        </button>
    </div>
</div>
```

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

Patrón establecido en `translations/job_list.html`:

```django
<nav id="tabs-items" class="bg-base-100 flex flex-row font-medium gap-1 p-1 rounded-default text-important md:w-auto *:flex *:flex-row *:gap-1 *:font-medium *:whitespace-nowrap *:items-center *:px-2.5 *:py-[5px] *:rounded-default *:hover:bg-base-700/[.06] dark:bg-white/[.06] *:dark:hover:bg-white/[.06] [&>.active]:bg-white [&>.active]:shadow-xs [&>.active]:dark:bg-base-700 [&>.active]:hover:bg-white [&>.active]:dark:hover:bg-base-700">
    {% for tab in filter_tabs %}
        <a href="{{ tab.url }}" class="{% if tab.active %}active{% endif %}">{{ tab.label }}</a>
    {% endfor %}
</nav>
```
