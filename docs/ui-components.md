# UI Components — Biblioteca de componentes

Componentes custom que extienden Unfold Admin. Todos viven en `templates/unfold/components/` e invocables con `{% component "unfold/components/nombre.html" with ... %}{% endcomponent %}`.

Requieren `{% load unfold %}` en el template que los invoca.

---

## Índice

| Componente | Archivo | Descripción breve |
|---|---|---|
| [Modal Content](#modal-content) | `modal_content.html` | Shell reutilizable para modales HTMX |
| [Toast](#toast) | `toast.html` | Notificación flash async |
| [Confirm Dialog](#confirm-dialog) | `confirm_dialog.html` | Dialog de confirmación simple o estricto |
| [Data List](#data-list) | `data_list.html` | Pares clave-valor de un objeto |
| [Empty State](#empty-state) | `empty_state.html` | Estado vacío con ícono y acción opcional |
| [Skeleton](#skeleton) | `skeleton.html` | Placeholder animado de carga async |
| [Page Header](#page-header) | `page_header.html` | Cabecera de página con breadcrumb opcional |
| [Filter Tabs](#filter-tabs) | `filter_tabs.html` | Tabs de filtro con conteos async |
| [Stat Card](#stat-card) | `stat_card.html` | Tarjeta KPI con trend opcional |
| [Inline Edit](#inline-edit) | `inline_edit.html` | Edición inline via HTMX PATCH |
| [Split Panel](#split-panel) | `split_panel.html` | Layout master-detail con detalle HTMX |
| [Copy to Clipboard](#copy-to-clipboard) | `copy_to_clipboard.html` | Copiar valor al portapapeles |

---

## Modal Content

**Archivo:** `templates/unfold/components/modal_content.html`

Shell reutilizable para el modal nativo de Unfold. Se usa como partial HTMX — la vista retorna este componente y Alpine abre el modal.

### Parámetros

| Parámetro | Tipo | Default | Descripción |
|---|---|---|---|
| `title` | string | requerido | Título del modal |
| `subtitle` | string | — | Subtítulo bajo el título |
| `icon` | string | — | Material Symbol en el header |
| `size` | `sm` \| `md` \| `lg` \| `xl` | `md` | Ancho del panel |
| `footer` | bool | `True` | Mostrar footer con botón Cerrar |
| `close_label` | string | `"Cerrar"` | Texto del botón cerrar |

### Uso

```django
{# partial HTMX — sin {% extends %} #}
{% load i18n unfold %}

{% component "unfold/components/modal_content.html" with title=_("Detalle") icon="info" size="lg" %}
    <p>Contenido del modal</p>
{% endcomponent %}
```

### Script requerido en el template padre

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
```

### Trigger en el template padre

```django
<button
    hx-get="{% url 'mi_modal_view' obj.pk %}"
    hx-target="#modal-content"
    hx-swap="innerHTML">
    Abrir
</button>
```

---

## Toast

**Archivo:** `templates/unfold/components/toast.html`

Notificación flash temporal para acciones HTMX async. Se incluye **una sola vez** en `base_site.html` (ya registrado). No reemplaza Django messages — ese sigue activo para redirects de formulario.

**Regla:** formulario + redirect → Django messages. Acción HTMX → Toast.

### Tipos

| Tipo | Color | Ícono |
|---|---|---|
| `success` | Verde | `check_circle` |
| `error` | Rojo | `cancel` |
| `warning` | Amarillo | `warning` |
| `info` | Azul | `info` |

### Uso — desde una vista Django

```python
import json

response["HX-Trigger"] = json.dumps({
    "showToast": {
        "type": "success",   # success | error | warning | info
        "title": "Guardado", # requerido
        "body": "Mensaje..."  # opcional
    }
})
```

### Uso — desde JavaScript

```javascript
window.dispatchEvent(new CustomEvent("showtoast", {
    detail: { type: "success", title: "Listo", body: "Operación completada" }
}));
```

> **Nota:** HTMX convierte el nombre del evento a minúsculas — `showToast` en el header llega como `showtoast` al DOM.

---

## Confirm Dialog

**Archivo:** `templates/unfold/components/confirm_dialog.html`

Dialog de confirmación para acciones destructivas. Dos modos: simple (botones) y estricto (requiere escribir un texto exacto).

### Parámetros

| Parámetro | Tipo | Default | Descripción |
|---|---|---|---|
| `title` | string | requerido | Título del dialog |
| `body` | string | — | Mensaje explicativo |
| `confirm_label` | string | `"Confirmar"` | Texto del botón de acción |
| `cancel_label` | string | `"Cancelar"` | Texto del botón cancelar |
| `danger` | bool | `False` | Botón rojo si `True` |
| `confirm_text` | string | — | Activa modo estricto — el usuario debe escribir este texto |
| `action_url` | string | — | URL del form action POST |
| `hx_delete` | string | — | URL para `hx-delete` HTMX |

### Uso simple

```django
{% load unfold %}
{% component "unfold/components/confirm_dialog.html"
   with title=_("Eliminar usuario")
        body=_("Esta acción no se puede deshacer.")
        confirm_label=_("Eliminar")
        danger=True
        action_url=delete_url %}
{% endcomponent %}
```

### Uso estricto

```django
{% load unfold %}
{% component "unfold/components/confirm_dialog.html"
   with title=_("Eliminar proyecto")
        body=_("Escribe el nombre del proyecto para confirmar.")
        confirm_text="mi-proyecto"
        confirm_label=_("Eliminar")
        danger=True
        action_url=delete_url %}
{% endcomponent %}
```

---

## Data List

**Archivo:** `templates/unfold/components/data_list.html`

Lista de pares clave-valor para mostrar detalles de un objeto. Dos layouts: horizontal (default) y grid.

### Parámetros del componente

| Parámetro | Tipo | Default | Descripción |
|---|---|---|---|
| `items` | list of dict | requerido | Lista de pares clave-valor |
| `layout` | `"horizontal"` \| `"grid"` | `"horizontal"` | Layout visual |

### Estructura de cada item

| Clave | Tipo | Descripción |
|---|---|---|
| `label` | string | Etiqueta del campo |
| `value` | any | Valor a mostrar |
| `type` | `"text"` \| `"badge"` \| `"date"` \| `"mono"` \| `"link"` | Renderizado del valor |
| `badge_type` | `"success"` \| `"warning"` \| `"danger"` \| `"info"` | Color del badge |
| `href` | string | URL (solo si `type="link"`) |
| `empty` | string | Texto si value es falsy (default: `"—"`) |

### Uso

```python
# Vista Django
context["detalle"] = [
    {"label": _("Nombre"), "value": obj.nombre},
    {"label": _("Email"), "value": obj.email},
    {"label": _("Rol"), "value": obj.rol, "type": "badge", "badge_type": "success"},
    {"label": _("ID"), "value": obj.uuid, "type": "mono"},
    {"label": _("Creado"), "value": obj.created_at, "type": "date"},
    {"label": _("Web"), "value": "ejemplo.com", "type": "link", "href": "https://ejemplo.com"},
    {"label": _("Vacío"), "value": None},
]
```

```django
{% load unfold %}

{# Horizontal (default) #}
{% component "unfold/components/card.html" with title=_("Detalle") %}
    {% component "unfold/components/data_list.html" with items=detalle %}{% endcomponent %}
{% endcomponent %}

{# Grid 2 columnas #}
{% component "unfold/components/data_list.html" with items=kpis layout="grid" %}{% endcomponent %}
```

---

## Empty State

**Archivo:** `templates/unfold/components/empty_state.html`

Estado vacío para listas, tablas y secciones sin datos.

### Parámetros

| Parámetro | Tipo | Default | Descripción |
|---|---|---|---|
| `icon` | string | `"inbox"` | Material Symbol |
| `title` | string | requerido | Texto principal |
| `subtitle` | string | — | Texto secundario |
| `action_label` | string | — | Texto del botón (requiere `action_url`) |
| `action_url` | string | — | URL del botón de acción |
| `class` | string | — | Clases extra para el contenedor |

### Uso

```django
{% load unfold %}

{# Sin acción #}
{% component "unfold/components/empty_state.html"
   with icon="inbox"
        title=_("Sin registros")
        subtitle=_("Cuando se agreguen aparecerán aquí.") %}
{% endcomponent %}

{# Con acción #}
{% component "unfold/components/empty_state.html"
   with icon="group"
        title=_("Sin usuarios")
        subtitle=_("Comienza creando el primero.")
        action_label=_("Crear usuario")
        action_url="/admin/core/user/add/" %}
{% endcomponent %}
```

---

## Skeleton

**Archivo:** `templates/unfold/components/skeleton.html`

Placeholder animado (shimmer) para contenido que carga async. Requiere `{% load core_tags %}`.

### Parámetros

| Parámetro | Tipo | Default | Descripción |
|---|---|---|---|
| `type` | `"lines"` \| `"table"` | `"lines"` | Forma del skeleton |
| `rows` | int | `3` | Número de filas |
| `cols` | int | `4` | Columnas (solo `type="table"`) |
| `avatar` | bool | `True` | Círculo avatar (solo `type="lines"`) |

### Uso

```django
{% load unfold %}

{# Lines — default #}
{% component "unfold/components/skeleton.html" with rows=3 %}{% endcomponent %}

{# Tabla #}
{% component "unfold/components/skeleton.html" with rows=5 type="table" cols=3 %}{% endcomponent %}

{# Sin avatar #}
{% component "unfold/components/skeleton.html" with rows=4 avatar=False %}{% endcomponent %}
```

### Patrón HTMX — mostrar mientras carga

```django
<div id="mi-lista"
     hx-get="{% url 'mi_vista' %}"
     hx-trigger="load"
     hx-swap="innerHTML">
    {% component "unfold/components/skeleton.html" with rows=5 type="table" cols=3 %}{% endcomponent %}
</div>
```

---

## Page Header

**Archivo:** `templates/unfold/components/page_header.html`

Cabecera de página para vistas custom. Título, subtítulo, breadcrumb opcional y slot de acciones.

### Parámetros

| Parámetro | Tipo | Default | Descripción |
|---|---|---|---|
| `title` | string | requerido | Título principal |
| `subtitle` | string | — | Texto secundario |
| `breadcrumbs` | list of dict | — | Navegación de migas de pan |

### Estructura de breadcrumbs

```python
context["crumbs"] = [
    {"label": _("Admin"), "url": "/admin/"},
    {"label": _("Usuarios"), "url": "/admin/core/user/"},
    {"label": "Sergio Rodríguez"},  # sin url = item activo
]
```

### Uso

```django
{% load unfold %}

{# Sin breadcrumb #}
{% component "unfold/components/page_header.html"
   with title=_("Usuarios") subtitle=_("Gestión de accesos") %}
    <a href="/admin/core/user/add/"
       class="inline-flex items-center gap-1.5 px-4 py-2 text-xs font-medium rounded-default bg-primary-600 hover:bg-primary-700 text-white transition-colors">
        <span class="material-symbols-outlined text-sm leading-none">add</span>
        {% trans "Crear" %}
    </a>
{% endcomponent %}

{# Con breadcrumb #}
{% component "unfold/components/page_header.html"
   with title=_("Sergio Rodríguez") subtitle=_("Admin · Activo") breadcrumbs=crumbs %}
{% endcomponent %}
```

---

## Filter Tabs

**Archivo:** `templates/unfold/components/filter_tabs.html`

Tabs de filtro con conteos cargados async via HTMX. Los badges muestran `···` mientras cargan.

### Parámetros de cada tab

| Clave | Tipo | Descripción |
|---|---|---|
| `label` | string | Texto del tab |
| `url` | string | URL al hacer click |
| `active` | bool | Tab activo actualmente |
| `count_url` | string | URL HTMX que retorna solo el número |
| `count_type` | `"success"` \| `"warning"` \| `"danger"` \| `"info"` \| `"neutral"` | Color del badge |

### Uso

```python
# Vista Django
context["tabs"] = [
    {
        "label": _("Todos"),
        "url": "?",
        "active": not request.GET.get("status"),
        "count_url": reverse("users_count") + "?status=",
        "count_type": "neutral",
    },
    {
        "label": _("Activos"),
        "url": "?status=active",
        "active": request.GET.get("status") == "active",
        "count_url": reverse("users_count") + "?status=active",
        "count_type": "success",
    },
]
```

```django
{% load unfold %}
{% component "unfold/components/filter_tabs.html" with tabs=tabs %}{% endcomponent %}
```

### Vista de conteo

```python
def users_count_view(request):
    status = request.GET.get("status")
    qs = User.objects.all()
    if status:
        qs = qs.filter(is_active=(status == "active"))
    return HttpResponse(str(qs.count()))
```

---

## Stat Card

**Archivo:** `templates/unfold/components/stat_card.html`

Tarjeta KPI con valor, ícono y trend opcional (↑↓ con porcentaje).

### Parámetros

| Parámetro | Tipo | Default | Descripción |
|---|---|---|---|
| `title` | string | requerido | Etiqueta del KPI |
| `value` | string \| int | requerido | Valor principal |
| `icon` | string | `"analytics"` | Material Symbol |
| `icon_color` | `"primary"` \| `"success"` \| `"warning"` \| `"danger"` \| `"info"` | `"primary"` | Color del ícono |
| `trend` | int \| float | — | Positivo=↑verde, negativo=↓rojo, 0=→gris |
| `trend_label` | string | — | Texto junto al trend |
| `href` | string | — | Convierte la card en enlace |

### Uso

```django
{% load unfold %}

{# Simple #}
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
   with title=_("Cancelaciones") value=23 icon="cancel" icon_color="danger"
        trend=-5 trend_label=_("vs mes anterior") %}
{% endcomponent %}
```

---

## Inline Edit

**Archivo:** `templates/unfold/components/inline_edit.html`

Edición de un campo directamente en la vista, sin modal ni redirect. HTMX PATCH + Alpine.

### Parámetros

| Parámetro | Tipo | Default | Descripción |
|---|---|---|---|
| `value` | string | requerido | Valor actual |
| `field` | string | requerido | Nombre del campo en el modelo |
| `url` | string | requerido | URL que recibe el PATCH |
| `field_type` | `"text"` \| `"select"` \| `"textarea"` | `"text"` | Tipo de input |
| `choices` | list de `[value, label]` | — | Opciones para `field_type="select"` |
| `placeholder` | string | — | Placeholder del input |
| `empty_text` | string | `"—"` | Texto si value es vacío |

### Uso

```django
{% load unfold %}

{# Texto #}
{% component "unfold/components/inline_edit.html"
   with value=obj.nombre field="nombre" url=patch_url %}
{% endcomponent %}

{# Select #}
{% component "unfold/components/inline_edit.html"
   with value=obj.estado field="estado" url=patch_url
        field_type="select" choices=estado_choices %}
{% endcomponent %}

{# Textarea #}
{% component "unfold/components/inline_edit.html"
   with value=obj.descripcion field="descripcion" url=patch_url
        field_type="textarea" %}
{% endcomponent %}
```

### Vista PATCH Django

```python
import json
from django.views.decorators.http import require_http_methods

@login_required
@require_http_methods(["PATCH"])
def mi_patch_view(request, pk):
    obj = get_object_or_404(MiModelo, pk=pk)
    data = json.loads(request.body)
    field = data.get("field")
    value = data.get("value")
    allowed_fields = {"nombre", "estado", "descripcion"}
    if field not in allowed_fields:
        return HttpResponse(status=400)
    setattr(obj, field, value)
    obj.save(update_fields=[field])
    return render(request, "unfold/components/inline_edit.html", {
        "value": getattr(obj, field),
        "field": field,
        "url": request.path,
        "field_type": data.get("field_type", "text"),
    })
```

### Comportamiento

- **Reposo:** valor + ícono lápiz visible al hover
- **Edición:** input con borde primario, botones ✓ y ✕
- **Guardar:** Enter (solo `text`) o click ✓ → HTMX PATCH → componente se re-renderiza
- **Cancelar:** Escape o click ✕ → restaura el valor sin request
- **Error:** borde rojo + mensaje "Error al guardar"

---

## Split Panel

**Archivo:** `templates/unfold/components/split_panel.html`

Layout master-detail de dos columnas. Lista a la izquierda, detalle a la derecha cargado via HTMX.

### Parámetros

| Parámetro | Tipo | Default | Descripción |
|---|---|---|---|
| `detail_target` | string | `"split-detail"` | ID del panel derecho |
| `list_title` | string | — | Título sobre la lista |
| `empty_icon` | string | `"article"` | Ícono del empty state inicial |
| `empty_title` | string | `"Selecciona un elemento"` | Texto del empty state inicial |

### Uso

```django
{% load unfold %}

{% component "unfold/components/split_panel.html" with list_title=_("Usuarios") %}
    {% for obj in object_list %}
        <a href="#"
           hx-get="{% url 'mi_detalle' obj.pk %}"
           hx-target="#split-detail"
           hx-swap="innerHTML"
           class="split-panel-item {% if obj.pk == selected_pk %}active{% endif %}">
            <span class="block font-medium text-sm text-gray-900 dark:text-white">
                {{ obj.get_full_name|default:obj.username }}
            </span>
            <span class="block text-xs text-gray-400 mt-0.5">{{ obj.email }}</span>
        </a>
    {% endfor %}
{% endcomponent %}
```

### Vista de detalle

```python
# Retorna partial HTML sin {% extends %}
def mi_detalle_view(request, pk):
    obj = get_object_or_404(MiModelo, pk=pk)
    return render(request, "mi_app/partials/detalle.html", {"obj": obj})
```

---

## Copy to Clipboard

**Archivo:** `templates/unfold/components/copy_to_clipboard.html`

Muestra un valor con botón de copia. El ícono cambia a ✓ por 2 segundos al copiar.

> **Nota:** `navigator.clipboard` requiere HTTPS o `localhost`. No funciona en HTTP en producción.

### Parámetros

| Parámetro | Tipo | Default | Descripción |
|---|---|---|---|
| `value` | string | requerido | Valor a copiar |
| `label` | string | — | Etiqueta sobre el valor |
| `show_value` | bool | `True` | Mostrar el valor junto al ícono |
| `truncate` | bool | `False` | Truncar valor largo con `…` |

### Uso

```django
{% load unfold %}

{# Básico #}
{% component "unfold/components/copy_to_clipboard.html"
   with value=obj.uuid %}
{% endcomponent %}

{# Con label #}
{% component "unfold/components/copy_to_clipboard.html"
   with value=api_token label=_("Token API") %}
{% endcomponent %}

{# Truncado #}
{% component "unfold/components/copy_to_clipboard.html"
   with value=jwt_token truncate=True %}
{% endcomponent %}

{# Solo ícono sin mostrar el valor #}
{% component "unfold/components/copy_to_clipboard.html"
   with value=obj.uuid show_value=False %}
{% endcomponent %}
```

---

## Template tag: `make_range`

**Archivo:** `apps/core/templatetags/core_tags.py`

Filtro que convierte un entero N en `range(N)` para iterar N veces en templates. Usado internamente por `skeleton.html`.

```django
{% load core_tags %}

{% for i in 5|make_range %}
    {# se ejecuta 5 veces #}
{% endfor %}
```

---

## Convención de archivos

```
templates/
  unfold/
    components/          ← componentes custom del proyecto
      modal_content.html
      toast.html
      confirm_dialog.html
      data_list.html
      empty_state.html
      skeleton.html
      page_header.html
      filter_tabs.html
      stat_card.html
      inline_edit.html
      split_panel.html
      copy_to_clipboard.html
    helpers/             ← helpers custom que extienden Unfold
      header.html
      userlinks_with_notifications.html
  partials/              ← fragments HTMX globales
  admin/
    base_site.html       ← Toast registrado aquí (una sola vez)

apps/
  core/
    templatetags/
      core_tags.py       ← make_range y otros filtros globales
```
