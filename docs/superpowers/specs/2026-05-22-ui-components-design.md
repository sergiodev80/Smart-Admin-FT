# UI Components — Spec de diseño

**Fecha:** 2026-05-22  
**Scope:** 3 componentes prioritarios para extender Unfold Admin

---

## Contexto

Smart Admin FT usa Unfold Admin como base de UI. Los componentes nativos de Unfold cubren el admin estándar, pero las vistas custom y acciones HTMX necesitan componentes propios. La convención establecida es `templates/unfold/components/` para que sean invocables con `{% component "unfold/components/nombre.html" %}`.

Ya existe: `modal_content.html` (creado previamente).

Este spec define los 3 siguientes componentes prioritarios.

---

## 1. Toast — `toast.html`

### Propósito
Feedback visual temporal para acciones HTMX async. **No reemplaza** `unfold/helpers/messages.html` — ese sigue activo para redirects de formulario clásicos.

**Regla:** formulario + redirect → Django messages. Acción HTMX → Toast.

### Diseño
- Posición: banner superior centrado, z-index sobre el contenido
- Un toast a la vez (el nuevo reemplaza al anterior)
- Auto-dismiss: 4 segundos
- Cierre manual con botón ×
- Animación: slide-down al aparecer, fade-out al desaparecer

### Tipos
| Tipo | Color borde-top | Ícono Material |
|------|----------------|----------------|
| `success` | `#22c55e` | `check_circle` |
| `error` | `#ef4444` | `cancel` |
| `warning` | `#f59e0b` | `warning` |
| `info` | `#3b82f6` | `info` |

### API — disparado desde Django via HX-Trigger
```python
import json
response["HX-Trigger"] = json.dumps({
    "showToast": {
        "type": "success",       # success | error | warning | info
        "title": "Guardado",     # requerido
        "body": "Mensaje..."     # opcional
    }
})
```

### Implementación
- **Template:** `templates/unfold/components/toast.html` — incluido una vez en `base_site.html`
- **JS:** listener `document.addEventListener("showToast", ...)` — Alpine o vanilla JS
- **Sin dependencias externas** — usa Alpine (ya incluido en Unfold) + CSS del proyecto

### Archivos a crear/modificar
- `templates/unfold/components/toast.html` — componente con Alpine x-data
- `templates/admin/base_site.html` — incluir el componente una vez

---

## 2. Dialog de confirmación — `confirm_dialog.html`

### Propósito
Confirmar acciones destructivas antes de ejecutarlas. Reutilizable desde cualquier vista o acción HTMX.

### Modos

**Modo simple (default)** — título + mensaje + 2 botones:
```django
{% component "unfold/components/confirm_dialog.html"
   with title=_("Eliminar usuario")
   body=_("Esta acción no se puede deshacer.")
   confirm_label=_("Eliminar")
   danger=True %}
{% endcomponent %}
```

**Modo estricto** — el usuario debe escribir un texto exacto para habilitar el botón de confirmación:
```django
{% component "unfold/components/confirm_dialog.html"
   with title=_("Eliminar proyecto")
   body=_("Escribe el nombre del proyecto para confirmar.")
   confirm_text="mi-proyecto"
   confirm_label=_("Eliminar")
   danger=True %}
{% endcomponent %}
```

### Parámetros
| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `title` | string | requerido | Título del dialog |
| `body` | string | — | Mensaje explicativo |
| `confirm_label` | string | `"Confirmar"` | Texto del botón de acción |
| `cancel_label` | string | `"Cancelar"` | Texto del botón cancelar |
| `danger` | bool | `False` | Botón rojo si `True`, primario si `False` |
| `confirm_text` | string | — | Si se pasa, activa modo estricto con input |
| `action_url` | string | — | URL del form action (submit POST) |
| `hx_delete` | string | — | Alternativa: `hx-delete` HTMX |

### Diseño
- Se renderiza dentro de `modal_content.html` (reutiliza el shell del modal)
- Ícono de advertencia en el header (🗑 para delete, ⚠ para danger genérico)
- Modo estricto: botón deshabilitado hasta que el input coincida exactamente con `confirm_text`
- Validación del input en Alpine (sin request al servidor)

### Archivos a crear
- `templates/unfold/components/confirm_dialog.html`

---

## 3. Data List — `data_list.html`

### Propósito
Mostrar pares clave-valor de un objeto de forma semántica y consistente. Alternativa legible a una tabla de una sola fila.

### Layouts

**Horizontal (default)** — etiqueta izquierda, valor derecha, separador entre filas:
```python
# Vista Python
context["detalle"] = [
    {"label": _("Nombre"), "value": obj.nombre},
    {"label": _("Email"), "value": obj.email},
    {"label": _("Rol"), "value": obj.rol, "type": "badge", "badge_type": "success"},
    {"label": _("Creado"), "value": obj.created_at, "type": "date"},
]
```

```django
{% component "unfold/components/data_list.html" with items=detalle %}{% endcomponent %}
```

**Grid (2 columnas)** — etiqueta arriba, valor abajo, mejor para pocos campos destacados:
```django
{% component "unfold/components/data_list.html" with items=kpis layout="grid" %}{% endcomponent %}
```

### Parámetros del componente
| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `items` | list of dict | requerido | Lista de pares clave-valor |
| `layout` | `"horizontal"` \| `"grid"` | `"horizontal"` | Layout visual |

### Estructura de cada item
| Clave | Tipo | Descripción |
|-------|------|-------------|
| `label` | string | Etiqueta del campo |
| `value` | any | Valor a mostrar |
| `type` | `"text"` \| `"badge"` \| `"date"` \| `"mono"` \| `"link"` | Renderizado del valor |
| `badge_type` | `"success"` \| `"warning"` \| `"danger"` \| `"info"` | Color del badge (solo si `type="badge"`) |
| `href` | string | URL (solo si `type="link"`) |
| `empty` | string | Texto si value es None/vacío, default `"—"` |

### Archivos a crear
- `templates/unfold/components/data_list.html`

---

## Convención de archivos

```
templates/
  unfold/
    components/
      modal_content.html    ✓ existente
      toast.html            ← nuevo
      confirm_dialog.html   ← nuevo
      data_list.html        ← nuevo
  admin/
    base_site.html          ← modificar: incluir toast una vez
```

---

## Componentes en backlog (seleccionados, pendientes de spec)

- Empty State
- Loading Skeleton
- Breadcrumb
- Page Header
- Split Panel
- Filter Tabs mejorado
- Stat Card mejorada
- Inline Edit
- Copy to Clipboard
