# UI Components Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Crear 3 componentes de UI reutilizables en `templates/unfold/components/` que extienden Unfold Admin: Toast, Dialog de confirmación y Data List.

**Architecture:** Cada componente vive en `templates/unfold/components/` e invocable con `{% component "unfold/components/nombre.html" %}`. Toast se registra una vez en `base_site.html` y escucha el evento HTMX `showToast`. Confirm Dialog reutiliza el shell de `modal_content.html`. Data List es un template puro sin JS.

**Tech Stack:** Django templates, Alpine.js (ya incluido en Unfold), HTMX `HX-Trigger`, Tailwind CSS (clases de Unfold), Material Symbols.

---

## Mapa de archivos

| Acción | Archivo |
|--------|---------|
| Crear | `templates/unfold/components/toast.html` |
| Crear | `templates/unfold/components/confirm_dialog.html` |
| Crear | `templates/unfold/components/data_list.html` |
| Modificar | `templates/admin/base_site.html` |

---

## Task 1: Toast — template y registro en base_site

**Files:**
- Create: `templates/unfold/components/toast.html`
- Modify: `templates/admin/base_site.html`

- [ ] **Step 1: Crear `toast.html`**

```django
{# templates/unfold/components/toast.html #}
{# Incluir UNA VEZ en base_site.html. Escucha el evento HTMX showToast. #}
{% load i18n %}

<div
  x-data="{
    show: false,
    type: 'info',
    title: '',
    body: '',
    timer: null,
    open(detail) {
      this.type = detail.type || 'info';
      this.title = detail.title || '';
      this.body = detail.body || '';
      this.show = true;
      clearTimeout(this.timer);
      this.timer = setTimeout(() => { this.show = false; }, 4000);
    }
  }"
  x-on:showtoast.window="open($event.detail)"
  x-show="show"
  x-transition:enter="transition ease-out duration-200"
  x-transition:enter-start="opacity-0 -translate-y-2"
  x-transition:enter-end="opacity-100 translate-y-0"
  x-transition:leave="transition ease-in duration-150"
  x-transition:leave-start="opacity-100 translate-y-0"
  x-transition:leave-end="opacity-0 -translate-y-2"
  style="display:none"
  class="fixed top-4 left-1/2 -translate-x-1/2 z-[9999] w-full max-w-sm pointer-events-auto"
  role="alert"
  aria-live="assertive"
>
  <div
    class="bg-white dark:bg-base-900 rounded-default shadow-lg border border-base-200 dark:border-base-700 overflow-hidden"
    :class="{
      'border-t-4 border-t-green-500':  type === 'success',
      'border-t-4 border-t-red-500':    type === 'error',
      'border-t-4 border-t-yellow-500': type === 'warning',
      'border-t-4 border-t-blue-500':   type === 'info'
    }"
  >
    <div class="flex items-start gap-3 px-4 py-3">
      <span
        class="material-symbols-outlined text-xl flex-shrink-0 mt-0.5"
        :class="{
          'text-green-500':  type === 'success',
          'text-red-500':    type === 'error',
          'text-yellow-500': type === 'warning',
          'text-blue-500':   type === 'info'
        }"
        x-text="type === 'success' ? 'check_circle' : type === 'error' ? 'cancel' : type === 'warning' ? 'warning' : 'info'"
      ></span>
      <div class="flex-1 min-w-0">
        <p class="text-sm font-semibold text-gray-900 dark:text-white" x-text="title"></p>
        <p class="text-xs text-gray-500 dark:text-gray-400 mt-0.5" x-text="body" x-show="body"></p>
      </div>
      <button
        type="button"
        x-on:click="show = false; clearTimeout(timer)"
        class="text-gray-400 hover:text-gray-600 dark:hover:text-gray-200 flex-shrink-0"
        aria-label="{% trans 'Cerrar' %}"
      >
        <span class="material-symbols-outlined text-lg leading-none">close</span>
      </button>
    </div>
  </div>
</div>
```

- [ ] **Step 2: Registrar toast en `base_site.html`**

Reemplazar el contenido actual de `templates/admin/base_site.html`:

```django
{% extends "admin/base.html" %}
{% load i18n unfold %}

{% block extrahead %}
  {{ block.super }}
  <script src="https://unpkg.com/htmx.org@2.0.4" integrity="sha384-HGfztofotfshcF7+8n44JQL2oJmowVChPTg48S+jvZoztPfvwD79OC/LTtG6dMp+" crossorigin="anonymous"></script>
{% endblock %}

{% block footer %}
  {{ block.super }}
  {% component "unfold/components/toast.html" %}{% endcomponent %}
{% endblock %}
```

- [ ] **Step 3: Verificar que Alpine escucha el evento**

Abrir el admin en el browser. En la consola del browser ejecutar:

```javascript
window.dispatchEvent(new CustomEvent("showtoast", {
  detail: { type: "success", title: "Prueba", body: "El toast funciona" }
}));
```

Debe aparecer el banner superior centrado y desaparecer a los 4 segundos.

- [ ] **Step 4: Verificar disparo desde Django via HX-Trigger**

En cualquier vista de prueba temporal, agregar:

```python
import json
from django.http import HttpResponse

def test_toast_view(request):
    response = HttpResponse("ok")
    response["HX-Trigger"] = json.dumps({
        "showToast": {"type": "success", "title": "Desde Django", "body": "HX-Trigger funciona"}
    })
    return response
```

Llamar la vista con HTMX desde cualquier botón de prueba. El toast debe aparecer.

> **Nota:** HTMX convierte el nombre del evento a minúsculas al dispararlo al DOM — `showToast` en el header llega como `showtoast` al listener de Alpine. El `x-on:showtoast.window` en el template ya lo maneja correctamente.

- [ ] **Step 5: Commit**

```bash
git add templates/unfold/components/toast.html templates/admin/base_site.html
git commit -m "feat(ui): add Toast component — HTMX showToast event, 4 tipos, banner superior"
```

---

## Task 2: Confirm Dialog — template reutilizando modal_content

**Files:**
- Create: `templates/unfold/components/confirm_dialog.html`

- [ ] **Step 1: Crear `confirm_dialog.html`**

```django
{# templates/unfold/components/confirm_dialog.html #}
{#
  Dialog de confirmación reutilizable. Dos modos:
  - Simple (default): título + mensaje + 2 botones
  - Estricto: requiere escribir confirm_text para habilitar el botón

  Parámetros:
    title        — string (requerido)
    body         — string (opcional)
    confirm_label — string (default: "Confirmar")
    cancel_label  — string (default: "Cancelar")
    danger        — bool (default: False) — botón rojo si True
    confirm_text  — string (opcional) — activa modo estricto
    action_url    — string (opcional) — form action POST
    hx_delete     — string (opcional) — hx-delete URL alternativa

  Uso simple:
    {% component "unfold/components/confirm_dialog.html"
       with title=_("Eliminar usuario") body=_("No se puede deshacer.") danger=True action_url=url %}
    {% endcomponent %}

  Uso estricto:
    {% component "unfold/components/confirm_dialog.html"
       with title=_("Eliminar proyecto") confirm_text="mi-proyecto" danger=True action_url=url %}
    {% endcomponent %}
#}
{% load i18n unfold %}

{% with confirm_label=confirm_label|default:_("Confirmar") %}
{% with cancel_label=cancel_label|default:_("Cancelar") %}

<div
  x-data="{
    input: '',
    required: '{{ confirm_text|escapejs }}',
    get canConfirm() {
      return this.required === '' || this.input === this.required;
    }
  }"
>
  {# Header #}
  <div class="flex items-start justify-between px-6 py-4 border-b border-base-200 dark:border-base-700">
    <div class="flex items-center gap-3">
      <span class="material-symbols-outlined text-xl flex-shrink-0
        {% if danger %}text-red-500{% else %}text-yellow-500{% endif %}">
        {% if danger %}delete{% else %}warning{% endif %}
      </span>
      <h2 class="text-base font-semibold text-gray-900 dark:text-white">{{ title }}</h2>
    </div>
    <button
      type="button"
      x-on:click="openModal = false"
      class="p-1.5 rounded-default text-gray-400 hover:bg-base-100 dark:hover:bg-base-800 transition-colors ml-4"
    >
      <span class="material-symbols-outlined text-xl leading-none">close</span>
    </button>
  </div>

  {# Body #}
  <div class="px-6 py-5">
    {% if body %}
      <p class="text-sm text-gray-600 dark:text-gray-300 mb-4">{{ body }}</p>
    {% endif %}

    {% if confirm_text %}
      <p class="text-sm text-gray-600 dark:text-gray-300 mb-3">
        {% blocktrans with text=confirm_text %}Escribe <strong>{{ text }}</strong> para confirmar.{% endblocktrans %}
      </p>
      <input
        type="text"
        x-model="input"
        placeholder="{{ confirm_text }}"
        class="w-full border border-base-200 dark:border-base-700 rounded-default px-3 py-2 text-sm bg-white dark:bg-base-800 text-gray-900 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
        autocomplete="off"
      >
    {% endif %}
  </div>

  {# Footer #}
  <div class="px-6 py-4 border-t border-base-200 dark:border-base-700 flex justify-end gap-3">
    <button
      type="button"
      x-on:click="openModal = false"
      class="px-4 py-2 text-sm font-medium rounded-default text-gray-600 dark:text-gray-300 hover:bg-base-100 dark:hover:bg-base-800 transition-colors"
    >
      {{ cancel_label }}
    </button>

    {% if action_url %}
      <form method="post" action="{{ action_url }}" class="inline">
        {% csrf_token %}
        <button
          type="submit"
          :disabled="!canConfirm"
          :class="canConfirm
            ? '{% if danger %}bg-red-600 hover:bg-red-700{% else %}bg-primary-600 hover:bg-primary-700{% endif %} text-white'
            : 'bg-gray-200 dark:bg-base-700 text-gray-400 cursor-not-allowed'"
          class="px-4 py-2 text-sm font-medium rounded-default transition-colors"
        >
          {{ confirm_label }}
        </button>
      </form>
    {% elif hx_delete %}
      <button
        type="button"
        hx-delete="{{ hx_delete }}"
        hx-confirm=""
        :disabled="!canConfirm"
        :class="canConfirm
          ? '{% if danger %}bg-red-600 hover:bg-red-700{% else %}bg-primary-600 hover:bg-primary-700{% endif %} text-white'
          : 'bg-gray-200 dark:bg-base-700 text-gray-400 cursor-not-allowed'"
        class="px-4 py-2 text-sm font-medium rounded-default transition-colors"
        x-on:click="if(canConfirm) openModal = false"
      >
        {{ confirm_label }}
      </button>
    {% else %}
      <button
        type="button"
        :disabled="!canConfirm"
        :class="canConfirm
          ? '{% if danger %}bg-red-600 hover:bg-red-700{% else %}bg-primary-600 hover:bg-primary-700{% endif %} text-white'
          : 'bg-gray-200 dark:bg-base-700 text-gray-400 cursor-not-allowed'"
        class="px-4 py-2 text-sm font-medium rounded-default transition-colors"
      >
        {{ confirm_label }}
      </button>
    {% endif %}
  </div>
</div>

{% endwith %}
{% endwith %}
```

- [ ] **Step 2: Verificar modo simple en browser**

En cualquier template de prueba, cargar el componente dentro del modal nativo de Unfold:

```django
{# En un partial HTMX de prueba #}
{% load i18n unfold %}
{% component "unfold/components/confirm_dialog.html"
   with title=_("Eliminar usuario")
   body=_("Esta acción no se puede deshacer.")
   confirm_label=_("Eliminar")
   danger=True
   action_url="/admin/" %}
{% endcomponent %}
```

Verificar: botón "Eliminar" visible y habilitado. Click en "Cancelar" cierra el modal.

- [ ] **Step 3: Verificar modo estricto en browser**

```django
{% component "unfold/components/confirm_dialog.html"
   with title=_("Eliminar proyecto")
   body=_("Esta acción eliminará todos los datos.")
   confirm_text="mi-proyecto"
   confirm_label=_("Eliminar")
   danger=True
   action_url="/admin/" %}
{% endcomponent %}
```

Verificar: botón "Eliminar" deshabilitado (gris) hasta escribir exactamente `mi-proyecto`. Al escribir el texto, el botón se habilita (rojo).

- [ ] **Step 4: Commit**

```bash
git add templates/unfold/components/confirm_dialog.html
git commit -m "feat(ui): add ConfirmDialog component — modo simple y estricto, Alpine validation"
```

---

## Task 3: Data List — template puro sin JS

**Files:**
- Create: `templates/unfold/components/data_list.html`

- [ ] **Step 1: Crear `data_list.html`**

```django
{# templates/unfold/components/data_list.html #}
{#
  Lista de pares clave-valor para mostrar detalles de un objeto.

  Parámetros:
    items  — list of dict (requerido) — ver estructura abajo
    layout — "horizontal" (default) | "grid"

  Estructura de cada item:
    label      — string: etiqueta visible
    value      — any: valor a mostrar
    type       — "text" (default) | "badge" | "date" | "mono" | "link"
    badge_type — "success" | "warning" | "danger" | "info" (solo si type="badge")
    href       — string URL (solo si type="link")
    empty      — string fallback si value es falsy (default "—")

  Uso horizontal (default):
    {% component "unfold/components/data_list.html" with items=detalle %}{% endcomponent %}

  Uso grid:
    {% component "unfold/components/data_list.html" with items=kpis layout="grid" %}{% endcomponent %}
#}
{% load i18n %}

{% with layout=layout|default:"horizontal" %}

{% if layout == "grid" %}
  {# ── Grid layout ── #}
  <dl class="grid grid-cols-2 gap-x-6 gap-y-5">
    {% for item in items %}
      {% with val=item.value|default:item.empty|default:"—" typ=item.type|default:"text" %}
      <div>
        <dt class="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400 mb-1">
          {{ item.label }}
        </dt>
        <dd>
          {% if typ == "badge" %}
            <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium
              {% if item.badge_type == 'success' %}bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400
              {% elif item.badge_type == 'warning' %}bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400
              {% elif item.badge_type == 'danger' %}bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400
              {% else %}bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400{% endif %}">
              {{ val }}
            </span>
          {% elif typ == "mono" %}
            <span class="font-mono text-xs text-gray-700 dark:text-gray-300">{{ val }}</span>
          {% elif typ == "link" %}
            <a href="{{ item.href }}" class="text-sm text-primary-600 dark:text-primary-400 hover:underline">{{ val }}</a>
          {% elif typ == "date" %}
            <time class="text-sm text-gray-700 dark:text-gray-300">{{ val }}</time>
          {% else %}
            <span class="text-sm text-gray-900 dark:text-white font-medium">{{ val }}</span>
          {% endif %}
        </dd>
      </div>
      {% endwith %}
    {% empty %}
      <div class="col-span-2 text-sm text-gray-400 dark:text-gray-500">{% trans "Sin datos." %}</div>
    {% endfor %}
  </dl>

{% else %}
  {# ── Horizontal layout (default) ── #}
  <dl class="divide-y divide-base-200 dark:divide-base-700">
    {% for item in items %}
      {% with val=item.value|default:item.empty|default:"—" typ=item.type|default:"text" %}
      <div class="flex items-center gap-4 py-3 first:pt-0 last:pb-0">
        <dt class="w-36 flex-shrink-0 text-sm font-medium text-gray-500 dark:text-gray-400">
          {{ item.label }}
        </dt>
        <dd class="flex-1 min-w-0">
          {% if typ == "badge" %}
            <span class="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium
              {% if item.badge_type == 'success' %}bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400
              {% elif item.badge_type == 'warning' %}bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-400
              {% elif item.badge_type == 'danger' %}bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400
              {% else %}bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400{% endif %}">
              {{ val }}
            </span>
          {% elif typ == "mono" %}
            <span class="font-mono text-xs text-gray-700 dark:text-gray-300 bg-base-100 dark:bg-base-800 px-1.5 py-0.5 rounded">{{ val }}</span>
          {% elif typ == "link" %}
            <a href="{{ item.href }}" class="text-sm text-primary-600 dark:text-primary-400 hover:underline truncate block">{{ val }}</a>
          {% elif typ == "date" %}
            <time class="text-sm text-gray-700 dark:text-gray-300">{{ val }}</time>
          {% else %}
            <span class="text-sm text-gray-900 dark:text-white">{{ val }}</span>
          {% endif %}
        </dd>
      </div>
      {% endwith %}
    {% empty %}
      <div class="py-3 text-sm text-gray-400 dark:text-gray-500">{% trans "Sin datos." %}</div>
    {% endfor %}
  </dl>
{% endif %}

{% endwith %}
```

- [ ] **Step 2: Verificar layout horizontal en browser**

En una vista de prueba, pasar el siguiente contexto:

```python
context["detalle_usuario"] = [
    {"label": "Nombre", "value": "Sergio Rodríguez"},
    {"label": "Email", "value": "sergio@ejemplo.com"},
    {"label": "Rol", "value": "Admin", "type": "badge", "badge_type": "success"},
    {"label": "ID", "value": "abc-123", "type": "mono"},
    {"label": "Creado", "value": "22 mayo 2026", "type": "date"},
    {"label": "Web", "value": "ejemplo.com", "type": "link", "href": "https://ejemplo.com"},
    {"label": "Vacío", "value": None},
]
```

```django
{% component "unfold/components/card.html" with title=_("Detalle") %}
  {% component "unfold/components/data_list.html" with items=detalle_usuario %}{% endcomponent %}
{% endcomponent %}
```

Verificar: etiqueta a la izquierda, valor a la derecha, badge verde para Rol, código monospace para ID, em dash para el campo vacío.

- [ ] **Step 3: Verificar layout grid en browser**

```python
context["kpis"] = [
    {"label": "Total usuarios", "value": "1,234"},
    {"label": "Estado", "value": "Activo", "type": "badge", "badge_type": "success"},
    {"label": "Plan", "value": "Pro"},
    {"label": "Renovación", "value": "01 jun 2026", "type": "date"},
]
```

```django
{% component "unfold/components/card.html" with title=_("Resumen") %}
  {% component "unfold/components/data_list.html" with items=kpis layout="grid" %}{% endcomponent %}
{% endcomponent %}
```

Verificar: 2 columnas, etiqueta pequeña arriba, valor prominente abajo.

- [ ] **Step 4: Commit**

```bash
git add templates/unfold/components/data_list.html
git commit -m "feat(ui): add DataList component — horizontal y grid layout, 5 tipos de valor"
```

---

## Self-review checklist

- [x] Toast: listener Alpine usa `showtoast` (lowercase) — HTMX convierte nombres de evento a minúsculas
- [x] Toast: incluido en `{% block footer %}` de base_site para no interferir con `{% block extrahead %}`
- [x] ConfirmDialog: `canConfirm` es `true` cuando `required === ''` (modo simple sin confirm_text)
- [x] ConfirmDialog: `hx-confirm=""` en el botón hx-delete evita el confirm nativo de HTMX
- [x] DataList: `item.value|default:item.empty|default:"—"` — fallback en dos niveles
- [x] Los 3 componentes usan clases Unfold (`rounded-default`, `base-200`, `base-900`) — consistencia con el design system
