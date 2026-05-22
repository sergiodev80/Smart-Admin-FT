# Empty State + Loading Skeleton — Spec de diseño

**Fecha:** 2026-05-22  
**Scope:** 2 componentes de feedback para extender Unfold Admin

---

## Contexto

Continuación del ciclo de componentes UI. Convención establecida: `templates/unfold/components/` invocables con `{% component "unfold/components/nombre.html" %}`. Íconos: `<span class="material-symbols-outlined">` (fuente expuesta por Unfold al desarrollador).

---

## 1. Empty State — `empty_state.html`

### Propósito
Mostrar un estado vacío consistente cuando una lista, tabla o sección no tiene datos. Guía al usuario con mensaje claro y acción opcional.

### Diseño
- Centrado verticalmente y horizontalmente en su contenedor
- Ícono Material Symbols grande (48px), tenue (opacity reducida)
- Título prominente + subtítulo opcional
- Botón de acción opcional — solo aparece si se pasan `action_label` + `action_url`
- Fondo transparente — hereda el fondo del contenedor padre (card, tabla, página)

### API
```django
{# Sin acción — lista de solo lectura #}
{% component "unfold/components/empty_state.html"
   with icon="inbox"
        title=_("Sin registros")
        subtitle=_("Cuando se agreguen aparecerán aquí.") %}
{% endcomponent %}

{# Con acción — CRUD #}
{% component "unfold/components/empty_state.html"
   with icon="group"
        title=_("Sin usuarios")
        subtitle=_("Comienza creando el primero.")
        action_label=_("Crear usuario")
        action_url="/admin/core/user/add/" %}
{% endcomponent %}
```

### Parámetros
| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `icon` | string | `"inbox"` | Nombre del Material Symbol |
| `title` | string | requerido | Texto principal |
| `subtitle` | string | — | Texto secundario explicativo |
| `action_label` | string | — | Texto del botón (requiere `action_url`) |
| `action_url` | string | — | URL del botón de acción |
| `class` | string | — | Clases extra para el contenedor |

### Archivos a crear
- `templates/unfold/components/empty_state.html`

---

## 2. Loading Skeleton — `skeleton.html`

### Propósito
Placeholder animado (shimmer) mientras carga contenido async con HTMX. Mejor UX que un spinner genérico — el usuario ve la forma del contenido antes de que llegue.

### Diseño
- Animación shimmer: gradiente que se desplaza de izquierda a derecha
- Dos tipos via parámetro `type`:
  - `"lines"` (default) — filas de texto con avatar circular opcional
  - `"table"` — cabecera + filas con columnas de ancho variable
- `rows` controla cuántas filas renderizar (default: 3)
- `cols` controla columnas en modo tabla (default: 4)
- La animación se define con `@keyframes` en el `<style>` del componente — sin CSS externo

### API
```django
{# 3 líneas de texto — default #}
{% component "unfold/components/skeleton.html" with rows=3 %}{% endcomponent %}

{# Tabla 5 filas x 4 columnas #}
{% component "unfold/components/skeleton.html" with rows=5 type="table" cols=4 %}{% endcomponent %}

{# Líneas sin avatar #}
{% component "unfold/components/skeleton.html" with rows=4 avatar=False %}{% endcomponent %}
```

### Parámetros
| Parámetro | Tipo | Default | Descripción |
|-----------|------|---------|-------------|
| `type` | `"lines"` \| `"table"` | `"lines"` | Forma del skeleton |
| `rows` | int | `3` | Número de filas |
| `cols` | int | `4` | Número de columnas (solo `type="table"`) |
| `avatar` | bool | `True` | Mostrar círculo avatar (solo `type="lines"`) |

### Patrón HTMX — mostrar skeleton mientras carga
```django
{# Contenedor que se reemplaza con el contenido real #}
<div id="mi-lista"
     hx-get="{% url 'mi_vista' %}"
     hx-trigger="load"
     hx-swap="innerHTML">
  {% component "unfold/components/skeleton.html" with rows=5 type="table" cols=3 %}{% endcomponent %}
</div>
```

### Archivos a crear
- `templates/unfold/components/skeleton.html`

---

## Convención de archivos actualizada

```
templates/
  unfold/
    components/
      modal_content.html   ✓ existente
      toast.html           ✓ existente
      confirm_dialog.html  ✓ existente
      data_list.html       ✓ existente
      empty_state.html     ← nuevo
      skeleton.html        ← nuevo
```
