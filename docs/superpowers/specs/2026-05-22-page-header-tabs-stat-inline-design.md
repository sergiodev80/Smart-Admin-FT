# Page Header + Filter Tabs + Stat Card + Inline Edit — Spec de diseño

**Fecha:** 2026-05-22  
**Scope:** 4 componentes UI — ronda 3

---

## Contexto

Continuación del ciclo de componentes. Convención: `templates/unfold/components/`, íconos con `<span class="material-symbols-outlined">`, template tag `make_range` disponible en `{% load core_tags %}`.

---

## 1. Page Header — `page_header.html`

### Propósito
Cabecera consistente para vistas custom fuera del admin estándar. Título, subtítulo, acciones y breadcrumb opcional.

### API
```django
{# Sin breadcrumb #}
{% component "unfold/components/page_header.html"
   with title=_("Usuarios") subtitle=_("Gestión de accesos") %}
  {# Slot de acciones — contenido del bloque #}
  <a href="/admin/core/user/add/" class="...">+ Crear</a>
{% endcomponent %}

{# Con breadcrumb #}
{% component "unfold/components/page_header.html"
   with title=_("Sergio Rodríguez") subtitle=_("Admin · Activo")
        breadcrumbs=crumbs %}
{% endcomponent %}
```

### Parámetros
| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `title` | string | requerido | Título principal |
| `subtitle` | string | — | Texto secundario bajo el título |
| `breadcrumbs` | list of dict | — | Si se pasa, muestra navegación arriba |

### Estructura de breadcrumbs
```python
context["crumbs"] = [
    {"label": _("Admin"), "url": "/admin/"},
    {"label": _("Usuarios"), "url": "/admin/core/user/"},
    {"label": "Sergio Rodríguez"},  # último item sin url = activo
]
```

### Diseño
- Breadcrumb: separador `/`, último item sin enlace (activo), color primario
- Título: `text-2xl font-bold`
- Acciones: slot via `{{ component_content }}` — el que invoca pone los botones
- Separador horizontal al final (`border-b`) para separar del contenido

### Archivos a crear
- `templates/unfold/components/page_header.html`

---

## 2. Filter Tabs — `filter_tabs.html`

### Propósito
Tabs de filtro reutilizables con conteos cargados de forma async via HTMX. Los tabs se renderizan primero sin conteos (skeleton de badge) y HTMX los carga después.

### API
```python
# Vista Django
context["tabs"] = [
    {
        "label": _("Todos"),
        "url": "?status=",
        "active": not request.GET.get("status"),
        "count_url": reverse("users_count") + "?status=",  # HTMX carga el conteo
    },
    {
        "label": _("Activos"),
        "url": "?status=active",
        "active": request.GET.get("status") == "active",
        "count_url": reverse("users_count") + "?status=active",
        "count_type": "success",  # color del badge: success | warning | danger | info | neutral
    },
    {
        "label": _("Inactivos"),
        "url": "?status=inactive",
        "active": request.GET.get("status") == "inactive",
        "count_url": reverse("users_count") + "?status=inactive",
        "count_type": "danger",
    },
]
```

```django
{% component "unfold/components/filter_tabs.html" with tabs=tabs %}{% endcomponent %}
```

### Parámetros de cada tab
| Clave | Tipo | Descripción |
|-------|------|-------------|
| `label` | string | Texto del tab |
| `url` | string | URL al hacer click |
| `active` | bool | Tab activo actualmente |
| `count_url` | string | URL HTMX que retorna solo el número (partial) |
| `count_type` | string | Color del badge: `success`, `warning`, `danger`, `info`, `neutral` (default) |

### Vista de conteo — retorna solo el número
```python
def users_count_view(request):
    status = request.GET.get("status")
    qs = User.objects.all()
    if status:
        qs = qs.filter(is_active=(status == "active"))
    return HttpResponse(str(qs.count()))
```

### Diseño
- Contenedor: `bg-base-100 rounded-default` — mismo estilo que los tabs existentes en el proyecto
- Tab activo: `bg-white shadow-xs dark:bg-base-700`
- Badge: skeleton gris claro mientras carga, reemplazado por el número al llegar HTMX
- `hx-trigger="load"` — carga automática al renderizar

### Archivos a crear
- `templates/unfold/components/filter_tabs.html`

---

## 3. Stat Card — `stat_card.html`

### Propósito
Tarjeta de KPI con valor principal, ícono y trend opcional (↑↓ con porcentaje vs periodo anterior).

### API
```django
{# Simple — sin trend #}
{% component "unfold/components/stat_card.html"
   with title=_("Pendientes") value=48 icon="inbox" %}
{% endcomponent %}

{# Con trend positivo #}
{% component "unfold/components/stat_card.html"
   with title=_("Usuarios activos") value="1,234" icon="group"
        trend=12 trend_label=_("vs mes anterior") %}
{% endcomponent %}

{# Con trend negativo #}
{% component "unfold/components/stat_card.html"
   with title=_("Cancelaciones") value=23 icon="cancel"
        trend=-5 trend_label=_("vs mes anterior") %}
{% endcomponent %}
```

### Parámetros
| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `title` | string | requerido | Etiqueta del KPI |
| `value` | string/int | requerido | Valor principal |
| `icon` | string | `"analytics"` | Material Symbol |
| `icon_color` | string | `"primary"` | `primary`, `success`, `warning`, `danger`, `info` |
| `trend` | int/float | — | Porcentaje vs periodo anterior. Positivo=verde, negativo=rojo |
| `trend_label` | string | — | Texto junto al trend (ej: "vs mes anterior") |
| `href` | string | — | Si se pasa, la card entera es un enlace |

### Diseño
- Fondo: card blanca con borde (`bg-white dark:bg-base-900 border border-base-200`)
- Ícono: círculo de color semántico con el Material Symbol adentro
- Trend positivo: `text-green-600` con flecha ↑
- Trend negativo: `text-red-500` con flecha ↓
- Trend 0: `text-gray-500` con `→`

### Archivos a crear
- `templates/unfold/components/stat_card.html`

---

## 4. Inline Edit — `inline_edit.html`

### Propósito
Editar un campo directamente en la vista sin abrir modal ni redirigir. Click en el valor → input/select/textarea → PATCH via HTMX → respuesta reemplaza el componente.

### API
```django
{# Texto #}
{% component "unfold/components/inline_edit.html"
   with value=obj.nombre field="nombre" url=patch_url %}
{% endcomponent %}

{# Select #}
{% component "unfold/components/inline_edit.html"
   with value=obj.get_estado_display field="estado" url=patch_url
        field_type="select" choices=estado_choices %}
{% endcomponent %}

{# Textarea #}
{% component "unfold/components/inline_edit.html"
   with value=obj.descripcion field="descripcion" url=patch_url
        field_type="textarea" %}
{% endcomponent %}
```

### Parámetros
| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `value` | string | requerido | Valor actual a mostrar |
| `field` | string | requerido | Nombre del campo en el modelo |
| `url` | string | requerido | URL que recibe el PATCH |
| `field_type` | `"text"` \| `"select"` \| `"textarea"` | `"text"` | Tipo de input |
| `choices` | list of `[value, label]` | — | Opciones para `field_type="select"` |
| `placeholder` | string | — | Placeholder del input |
| `empty_text` | string | `"—"` | Texto si value es vacío |

### Vista Django — recibe el PATCH
```python
from django.views.decorators.http import require_http_methods
import json

@login_required
@require_http_methods(["PATCH"])
def user_patch_view(request, pk):
    obj = get_object_or_404(MiModelo, pk=pk)
    data = json.loads(request.body)
    field = data.get("field")
    value = data.get("value")
    # validar que field es editable
    allowed_fields = {"nombre", "estado", "descripcion"}
    if field not in allowed_fields:
        return HttpResponse(status=400)
    setattr(obj, field, value)
    obj.save(update_fields=[field])
    # retornar el componente actualizado
    return render(request, "unfold/components/inline_edit.html", {
        "value": getattr(obj, field),
        "field": field,
        "url": request.path,
        "field_type": data.get("field_type", "text"),
    })
```

### Diseño y comportamiento (Alpine + HTMX)
- **Estado reposo:** valor + ícono lápiz pequeño al hacer hover
- **Estado edición:** input/select/textarea con borde primario, botón ✓ y ✕
- **Guardando:** spinner mientras HTMX espera respuesta
- **Éxito:** HTMX reemplaza el componente con `hx-swap="outerHTML"` — el componente se re-renderiza con el nuevo valor
- **Error:** borde rojo + mensaje breve
- Cancelar con Escape o click en ✕ — restaura el valor original sin request

### Archivos a crear
- `templates/unfold/components/inline_edit.html`

---

## Convención actualizada

```
templates/unfold/components/
  modal_content.html    ✓
  toast.html            ✓
  confirm_dialog.html   ✓
  data_list.html        ✓
  empty_state.html      ✓
  skeleton.html         ✓
  page_header.html      ← nuevo
  filter_tabs.html      ← nuevo
  stat_card.html        ← nuevo
  inline_edit.html      ← nuevo
```
