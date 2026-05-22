# Split Panel + Copy to Clipboard — Spec de diseño

**Fecha:** 2026-05-22  
**Scope:** 2 componentes UI — ronda final

---

## 1. Split Panel — `split_panel.html`

### Propósito
Layout master-detail de dos columnas. Lista de items a la izquierda, detalle del item seleccionado a la derecha. El detalle se carga via HTMX al hacer click en una fila — sin reload de página.

### Diseño
- Columna izquierda: 35% de ancho, scrollable, lista de items clicables
- Columna derecha: 65%, área de detalle reemplazada por HTMX
- Item activo: borde izquierdo de color primario + fondo tenue
- En mobile: columnas apiladas verticalmente
- Estado inicial: detalle vacío con Empty State hasta que el usuario seleccione un item

### API
```django
{# Template de la página #}
{% component "unfold/components/split_panel.html"
   with detail_url=detail_url detail_target="split-detail" %}
  {# Slot: lista de items — cada item con hx-get al detalle #}
  {% for obj in object_list %}
    <a href="#"
       hx-get="{% url 'mi_detalle' obj.pk %}"
       hx-target="#split-detail"
       hx-swap="innerHTML"
       class="split-panel-item {% if obj.pk == selected_pk %}active{% endif %}">
      <span class="font-medium text-sm">{{ obj.nombre }}</span>
      <span class="text-xs text-gray-400">{{ obj.email }}</span>
    </a>
  {% endfor %}
{% endcomponent %}
```

```python
# Vista de detalle — retorna partial HTML
def mi_detalle_view(request, pk):
    obj = get_object_or_404(MiModelo, pk=pk)
    return render(request, "mi_app/partials/detalle.html", {"obj": obj})
```

### Parámetros del componente
| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `detail_target` | string | `"split-detail"` | ID del panel derecho (target HTMX) |
| `list_title` | string | — | Título opcional sobre la lista |
| `empty_icon` | string | `"article"` | Ícono del empty state inicial del detalle |
| `empty_title` | string | `"Selecciona un elemento"` | Texto del empty state inicial |

### Archivos a crear
- `templates/unfold/components/split_panel.html`

---

## 2. Copy to Clipboard — `copy_to_clipboard.html`

### Propósito
Mostrar un valor (ID, token, URL) con un botón de copia al portapapeles. Al hacer click, el ícono cambia a ✓ por 2 segundos como feedback visual. Sin Toast (el ícono es suficiente).

### Diseño
- Valor en `font-mono` con fondo tenue
- Ícono `content_copy` de Material Symbols junto al valor
- Al copiar: ícono cambia a `check` en verde por 2 segundos, luego vuelve
- Alpine.js para el estado — sin JS externo

### API
```django
{# Uso básico #}
{% component "unfold/components/copy_to_clipboard.html"
   with value=obj.uuid %}
{% endcomponent %}

{# Con label #}
{% component "unfold/components/copy_to_clipboard.html"
   with value=api_token label=_("Token API") %}
{% endcomponent %}

{# Solo ícono, sin mostrar el valor #}
{% component "unfold/components/copy_to_clipboard.html"
   with value=obj.uuid show_value=False %}
{% endcomponent %}
```

### Parámetros
| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `value` | string | requerido | Valor a copiar |
| `label` | string | — | Etiqueta sobre el valor |
| `show_value` | bool | `True` | Mostrar el valor junto al botón |
| `truncate` | bool | `False` | Truncar valor largo con `…` |

### Archivos a crear
- `templates/unfold/components/copy_to_clipboard.html`

---

## Convención final

```
templates/unfold/components/
  modal_content.html    ✓
  toast.html            ✓
  confirm_dialog.html   ✓
  data_list.html        ✓
  empty_state.html      ✓
  skeleton.html         ✓
  page_header.html      ✓
  filter_tabs.html      ✓
  stat_card.html        ✓
  inline_edit.html      ✓
  split_panel.html      ← nuevo
  copy_to_clipboard.html ← nuevo
```
