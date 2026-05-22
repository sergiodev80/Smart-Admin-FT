# Split Panel + Copy to Clipboard Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Crear los 2 últimos componentes UI — `split_panel.html` y `copy_to_clipboard.html` — completando la biblioteca de componentes del proyecto.

**Architecture:** `split_panel.html` es un layout de dos columnas donde el slot izquierdo lo rellena el caller con items HTMX. `copy_to_clipboard.html` usa Alpine.js para cambiar el ícono al copiar — sin dependencias externas.

**Tech Stack:** Django templates, Alpine.js, HTMX, Material Symbols, clases Unfold/Tailwind.

---

## Mapa de archivos

| Acción | Archivo |
|--------|---------|
| Crear | `templates/unfold/components/split_panel.html` |
| Crear | `templates/unfold/components/copy_to_clipboard.html` |

---

## Task 1: Split Panel — `split_panel.html`

**Files:**
- Create: `templates/unfold/components/split_panel.html`

- [ ] **Step 1: Crear `split_panel.html`**

```django
{# templates/unfold/components/split_panel.html #}
{#
  Layout master-detail de dos columnas.
  Columna izquierda: lista de items (slot via component_content).
  Columna derecha: detalle cargado async via HTMX.

  Parámetros:
    detail_target — string (default: "split-detail") — ID del panel derecho
    list_title    — string (opcional) — título sobre la lista
    empty_icon    — string (default: "article") — ícono del empty state inicial
    empty_title   — string (default: "Selecciona un elemento") — texto empty state

  Uso:
    {% component "unfold/components/split_panel.html" with list_title=_("Usuarios") %}
      {% for obj in object_list %}
        <a href="#"
           hx-get="{% url 'mi_detalle' obj.pk %}"
           hx-target="#split-detail"
           hx-swap="innerHTML"
           class="split-panel-item {% if obj.pk == selected_pk %}active{% endif %}">
          <span class="block font-medium text-sm text-gray-900 dark:text-white">{{ obj }}</span>
        </a>
      {% endfor %}
    {% endcomponent %}

  Vista de detalle (retorna partial HTML sin extends):
    def mi_detalle_view(request, pk):
        obj = get_object_or_404(MiModelo, pk=pk)
        return render(request, "mi_app/partials/detalle.html", {"obj": obj})
#}
{% load i18n unfold %}

{% with detail_target=detail_target|default:"split-detail" empty_icon=empty_icon|default:"article" %}
{% with empty_title=empty_title|default:_("Selecciona un elemento") %}

<style>
  .split-panel-item {
    display: block;
    padding: 10px 16px;
    border-left: 3px solid transparent;
    transition: background-color 0.15s, border-color 0.15s;
    cursor: pointer;
    text-decoration: none;
  }
  .split-panel-item:hover {
    background-color: rgb(var(--color-base-50, 248 250 252));
  }
  .dark .split-panel-item:hover {
    background-color: rgba(255,255,255,0.04);
  }
  .split-panel-item.active {
    border-left-color: rgb(var(--color-primary-600, 79 70 229));
    background-color: rgb(var(--color-primary-50, 238 242 255));
  }
  .dark .split-panel-item.active {
    background-color: rgba(var(--color-primary-900, 30 27 75), 0.3);
  }
</style>

<div class="flex flex-col md:flex-row border border-base-200 dark:border-base-700 rounded-default overflow-hidden bg-white dark:bg-base-900">

  {# Columna izquierda — lista #}
  <div class="w-full md:w-[35%] border-b md:border-b-0 md:border-r border-base-200 dark:border-base-700 flex flex-col">
    {% if list_title %}
      <div class="px-4 py-3 border-b border-base-200 dark:border-base-700 bg-base-50 dark:bg-base-800/50">
        <h3 class="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400">
          {{ list_title }}
        </h3>
      </div>
    {% endif %}
    <div class="overflow-y-auto flex-1 divide-y divide-base-100 dark:divide-base-800">
      {{ component_content }}
    </div>
  </div>

  {# Columna derecha — detalle #}
  <div id="{{ detail_target }}" class="flex-1 overflow-y-auto">
    {# Empty state inicial — reemplazado por HTMX al seleccionar un item #}
    {% component "unfold/components/empty_state.html"
       with icon=empty_icon title=empty_title %}
    {% endcomponent %}
  </div>

</div>

{% endwith %}
{% endwith %}
```

- [ ] **Step 2: Verificar layout en browser**

En una vista de prueba con contexto mínimo:

```python
from django.contrib.auth import get_user_model
User = get_user_model()

def test_split_view(request):
    from django.contrib import admin
    context = {"users": User.objects.all()[:10]}
    context.update(admin.site.each_context(request))
    return render(request, "test_split.html", context)
```

Template de prueba `test_split.html`:
```django
{% extends "unfold/layouts/base.html" %}
{% load i18n unfold %}

{% block content %}
{% component "unfold/components/split_panel.html" with list_title=_("Usuarios") %}
  {% for user in users %}
    <a href="#"
       hx-get="/test/user/{{ user.pk }}/"
       hx-target="#split-detail"
       hx-swap="innerHTML"
       class="split-panel-item">
      <span class="block font-medium text-sm text-gray-900 dark:text-white">{{ user.get_full_name|default:user.username }}</span>
      <span class="block text-xs text-gray-400 mt-0.5">{{ user.email }}</span>
    </a>
  {% endfor %}
{% endcomponent %}
{% endblock %}
```

Verificar: dos columnas visibles, lista a la izquierda con items, panel derecho con empty state "Selecciona un elemento". En mobile: columnas apiladas.

- [ ] **Step 3: Commit**

```bash
git add templates/unfold/components/split_panel.html
git commit -m "feat(ui): add SplitPanel component — master-detail HTMX, empty state inicial, responsive"
```

---

## Task 2: Copy to Clipboard — `copy_to_clipboard.html`

**Files:**
- Create: `templates/unfold/components/copy_to_clipboard.html`

- [ ] **Step 1: Crear `copy_to_clipboard.html`**

```django
{# templates/unfold/components/copy_to_clipboard.html #}
{#
  Valor con botón de copia al portapapeles. Ícono cambia a ✓ por 2 segundos al copiar.

  Parámetros:
    value      — string (requerido): valor a copiar
    label      — string (opcional): etiqueta sobre el valor
    show_value — bool (default: True): mostrar el valor junto al ícono
    truncate   — bool (default: False): truncar valor largo con …

  Uso básico:
    {% component "unfold/components/copy_to_clipboard.html"
       with value=obj.uuid %}
    {% endcomponent %}

  Con label:
    {% component "unfold/components/copy_to_clipboard.html"
       with value=api_token label=_("Token API") %}
    {% endcomponent %}

  Solo ícono:
    {% component "unfold/components/copy_to_clipboard.html"
       with value=obj.uuid show_value=False %}
    {% endcomponent %}
#}
{% load i18n %}

<div
  x-data="{
    copied: false,
    timer: null,
    copy() {
      navigator.clipboard.writeText('{{ value|escapejs }}').then(() => {
        this.copied = true;
        clearTimeout(this.timer);
        this.timer = setTimeout(() => { this.copied = false; }, 2000);
      });
    }
  }"
  class="inline-flex flex-col gap-1"
>
  {% if label %}
    <span class="text-xs font-medium text-gray-500 dark:text-gray-400">{{ label }}</span>
  {% endif %}

  <div class="inline-flex items-center gap-1.5 group">
    {% if show_value != False %}
      <span class="font-mono text-xs text-gray-700 dark:text-gray-300
                   bg-base-100 dark:bg-base-800 px-2 py-1 rounded
                   {% if truncate %}max-w-[180px] truncate{% endif %}"
            title="{{ value }}">
        {{ value }}
      </span>
    {% endif %}

    <button
      type="button"
      x-on:click="copy()"
      :class="copied ? 'text-green-500' : 'text-gray-400 hover:text-gray-600 dark:hover:text-gray-200'"
      class="transition-colors p-0.5 rounded focus:outline-none focus:ring-2 focus:ring-primary-500"
      :aria-label="copied ? '{% trans 'Copiado' %}' : '{% trans 'Copiar' %}'"
      :title="copied ? '{% trans 'Copiado' %}' : '{% trans 'Copiar' %}'"
    >
      <span class="material-symbols-outlined text-base leading-none"
            x-text="copied ? 'check' : 'content_copy'"></span>
    </button>
  </div>
</div>
```

- [ ] **Step 2: Verificar en browser**

En cualquier template de prueba:

```django
{% load unfold %}

{# Básico #}
{% component "unfold/components/copy_to_clipboard.html"
   with value="abc-123-def-456-xyz" %}
{% endcomponent %}

{# Con label #}
{% component "unfold/components/copy_to_clipboard.html"
   with value="sk-prod-abc123xyz789" label=_("Token API") %}
{% endcomponent %}

{# Truncado #}
{% component "unfold/components/copy_to_clipboard.html"
   with value="eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0.abc" truncate=True %}
{% endcomponent %}

{# Solo ícono #}
{% component "unfold/components/copy_to_clipboard.html"
   with value="abc-123" show_value=False %}
{% endcomponent %}
```

Verificar:
- Click en ícono → ícono cambia a ✓ verde
- Después de 2 segundos → vuelve al ícono de copiar
- El valor se puede pegar en cualquier campo de texto
- Versión truncada muestra `…` y el `title` tiene el valor completo

- [ ] **Step 3: Commit**

```bash
git add templates/unfold/components/copy_to_clipboard.html
git commit -m "feat(ui): add CopyToClipboard component — ícono ✓ feedback, Alpine, truncate opcional"
```

---

## Self-review

- [x] `split_panel.html` — `empty_state.html` ya existe en el proyecto, reutilizado correctamente
- [x] `split_panel.html` — `detail_target` como parámetro permite múltiples split panels en la misma página
- [x] `split_panel.html` — CSS inline con `:root` variables para compatibilidad dark mode sin clases Tailwind dinámicas
- [x] `copy_to_clipboard.html` — `navigator.clipboard` requiere HTTPS o localhost — funciona en dev y prod con SSL
- [x] `copy_to_clipboard.html` — `show_value != False` (no `not show_value`) para que el default `True` funcione correctamente en Django templates
- [x] Ningún componente requiere migraciones ni vistas nuevas
