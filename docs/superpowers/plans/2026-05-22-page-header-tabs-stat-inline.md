# Page Header + Filter Tabs + Stat Card + Inline Edit Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Crear 4 componentes UI — `page_header.html`, `filter_tabs.html`, `stat_card.html`, `inline_edit.html` — en `templates/unfold/components/`.

**Architecture:** Tres componentes son templates puros Django. `inline_edit.html` usa Alpine para estado local + HTMX PATCH para persistir — requiere una vista Django de ejemplo documentada pero no implementada (cada app define la suya). `filter_tabs.html` usa HTMX `hx-trigger="load"` para cargar conteos async.

**Tech Stack:** Django templates, Alpine.js, HTMX, Material Symbols, Tailwind/clases Unfold, `{% load core_tags %}` para `make_range`.

---

## Mapa de archivos

| Acción | Archivo |
|--------|---------|
| Crear | `templates/unfold/components/page_header.html` |
| Crear | `templates/unfold/components/filter_tabs.html` |
| Crear | `templates/unfold/components/stat_card.html` |
| Crear | `templates/unfold/components/inline_edit.html` |

---

## Task 1: Page Header — `page_header.html`

**Files:**
- Create: `templates/unfold/components/page_header.html`

- [ ] **Step 1: Crear `page_header.html`**

```django
{# templates/unfold/components/page_header.html #}
{#
  Cabecera de página reutilizable para vistas custom fuera del admin estándar.

  Parámetros:
    title       — string (requerido)
    subtitle    — string (opcional)
    breadcrumbs — list of dict (opcional): [{"label": "...", "url": "..."}, ...]
                  El último item sin "url" se trata como activo (no enlace).

  Slot de acciones: usa {{ component_content }} para botones/links.

  Uso sin breadcrumb:
    {% component "unfold/components/page_header.html"
       with title=_("Usuarios") subtitle=_("Gestión de accesos") %}
      <a href="/admin/core/user/add/">+ Crear</a>
    {% endcomponent %}

  Uso con breadcrumb:
    {% component "unfold/components/page_header.html"
       with title=_("Sergio") breadcrumbs=crumbs %}
    {% endcomponent %}

  Estructura de breadcrumbs:
    context["crumbs"] = [
        {"label": _("Admin"), "url": "/admin/"},
        {"label": _("Usuarios"), "url": "/admin/core/user/"},
        {"label": "Sergio Rodríguez"},  # sin url = activo
    ]
#}
{% load i18n %}

<div class="mb-6 border-b border-base-200 dark:border-base-700 pb-4">

  {% if breadcrumbs %}
    <nav class="flex items-center gap-1.5 text-xs text-gray-400 dark:text-gray-500 mb-3" aria-label="{% trans 'Breadcrumb' %}">
      {% for crumb in breadcrumbs %}
        {% if not forloop.last %}
          {% if crumb.url %}
            <a href="{{ crumb.url }}" class="hover:text-primary-600 dark:hover:text-primary-400 transition-colors">{{ crumb.label }}</a>
          {% else %}
            <span>{{ crumb.label }}</span>
          {% endif %}
          <span class="text-gray-300 dark:text-gray-600">/</span>
        {% else %}
          <span class="text-primary-600 dark:text-primary-400 font-medium">{{ crumb.label }}</span>
        {% endif %}
      {% endfor %}
    </nav>
  {% endif %}

  <div class="flex items-start justify-between gap-4">
    <div>
      <h1 class="text-2xl font-bold text-gray-900 dark:text-white leading-tight">{{ title }}</h1>
      {% if subtitle %}
        <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">{{ subtitle }}</p>
      {% endif %}
    </div>
    {% if component_content %}
      <div class="flex items-center gap-2 flex-shrink-0 mt-1">
        {{ component_content }}
      </div>
    {% endif %}
  </div>

</div>
```

- [ ] **Step 2: Verificar sin breadcrumb**

En cualquier template de prueba:

```django
{% load unfold %}
{% component "unfold/components/page_header.html"
   with title=_("Usuarios") subtitle=_("Gestión de accesos") %}
  <a href="/admin/core/user/add/"
     class="inline-flex items-center gap-1.5 px-4 py-2 text-xs font-medium rounded-default bg-primary-600 hover:bg-primary-700 text-white transition-colors">
    <span class="material-symbols-outlined text-sm leading-none">add</span>
    {% trans "Crear usuario" %}
  </a>
{% endcomponent %}
```

Verificar: título grande a la izquierda, botón a la derecha, separador horizontal al fondo. Sin breadcrumb.

- [ ] **Step 3: Verificar con breadcrumb**

```python
context["crumbs"] = [
    {"label": "Admin", "url": "/admin/"},
    {"label": "Usuarios", "url": "/admin/core/user/"},
    {"label": "Sergio Rodríguez"},
]
```

```django
{% load unfold %}
{% component "unfold/components/page_header.html"
   with title="Sergio Rodríguez" subtitle="Admin · Activo" breadcrumbs=crumbs %}
{% endcomponent %}
```

Verificar: breadcrumb arriba con separadores `/`, último item en color primario sin enlace.

- [ ] **Step 4: Commit**

```bash
git add templates/unfold/components/page_header.html
git commit -m "feat(ui): add PageHeader component — título, subtítulo, breadcrumb opcional, slot de acciones"
```

---

## Task 2: Filter Tabs — `filter_tabs.html`

**Files:**
- Create: `templates/unfold/components/filter_tabs.html`

- [ ] **Step 1: Crear `filter_tabs.html`**

```django
{# templates/unfold/components/filter_tabs.html #}
{#
  Tabs de filtro con conteos cargados async via HTMX.

  Parámetros:
    tabs — list of dict (requerido):
      label      — string: texto del tab
      url        — string: URL al hacer click
      active     — bool: tab activo actualmente
      count_url  — string (opcional): URL HTMX que retorna solo el número
      count_type — string (opcional): color del badge
                   "success" | "warning" | "danger" | "info" | "neutral" (default)

  Uso:
    {% component "unfold/components/filter_tabs.html" with tabs=tabs %}{% endcomponent %}

  Vista de conteo (retorna solo el número como texto plano):
    def mi_count_view(request):
        return HttpResponse(str(MiModelo.objects.filter(...).count()))
#}
{% load i18n %}

<nav class="bg-base-100 dark:bg-white/[.06] flex flex-row font-medium gap-1 p-1 rounded-default text-sm md:w-auto"
     aria-label="{% trans 'Filtros' %}">
  {% for tab in tabs %}
    <a href="{{ tab.url }}"
       class="flex flex-row gap-1.5 font-medium whitespace-nowrap items-center px-2.5 py-[5px] rounded-default
              hover:bg-base-700/[.06] dark:hover:bg-white/[.06] transition-colors
              {% if tab.active %}bg-white shadow-xs dark:bg-base-700 hover:bg-white dark:hover:bg-base-700{% endif %}">
      {{ tab.label }}
      {% if tab.count_url %}
        <span
          hx-get="{{ tab.count_url }}"
          hx-trigger="load"
          hx-swap="innerHTML"
          class="inline-flex items-center justify-center min-w-[18px] h-[18px] px-1 rounded-full text-xs font-semibold
                 {% if tab.count_type == 'success' %}bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400
                 {% elif tab.count_type == 'warning' %}bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400
                 {% elif tab.count_type == 'danger' %}bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400
                 {% elif tab.count_type == 'info' %}bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400
                 {% else %}bg-base-200 text-gray-600 dark:bg-base-700 dark:text-gray-300{% endif %}"
        >···</span>
      {% endif %}
    </a>
  {% endfor %}
</nav>
```

- [ ] **Step 2: Verificar tabs estáticos (sin count_url)**

```python
context["tabs"] = [
    {"label": "Todos", "url": "?", "active": True},
    {"label": "Activos", "url": "?status=active", "active": False},
    {"label": "Inactivos", "url": "?status=inactive", "active": False},
]
```

```django
{% load unfold %}
{% component "unfold/components/filter_tabs.html" with tabs=tabs %}{% endcomponent %}
```

Verificar: 3 tabs, el primero con fondo blanco y sombra (activo), los otros grises.

- [ ] **Step 3: Verificar tabs con conteos async**

Agregar una URL temporal de prueba en cualquier `urls.py`:

```python
from django.http import HttpResponse
from django.urls import path

def count_all(request): return HttpResponse("142")
def count_active(request): return HttpResponse("98")
def count_inactive(request): return HttpResponse("44")

urlpatterns += [
    path("test/count/all/", count_all, name="test_count_all"),
    path("test/count/active/", count_active, name="test_count_active"),
    path("test/count/inactive/", count_inactive, name="test_count_inactive"),
]
```

```python
context["tabs"] = [
    {"label": "Todos", "url": "?", "active": True,
     "count_url": "/test/count/all/", "count_type": "neutral"},
    {"label": "Activos", "url": "?status=active", "active": False,
     "count_url": "/test/count/active/", "count_type": "success"},
    {"label": "Inactivos", "url": "?status=inactive", "active": False,
     "count_url": "/test/count/inactive/", "count_type": "danger"},
]
```

Verificar: badges muestran `···` inicialmente, luego HTMX los reemplaza con 142, 98, 44.

- [ ] **Step 4: Commit**

```bash
git add templates/unfold/components/filter_tabs.html
git commit -m "feat(ui): add FilterTabs component — conteos async HTMX, badge semántico por tab"
```

---

## Task 3: Stat Card — `stat_card.html`

**Files:**
- Create: `templates/unfold/components/stat_card.html`

- [ ] **Step 1: Crear `stat_card.html`**

```django
{# templates/unfold/components/stat_card.html #}
{#
  Tarjeta de KPI con valor principal, ícono y trend opcional.

  Parámetros:
    title       — string (requerido)
    value       — string|int (requerido)
    icon        — string Material Symbol (default: "analytics")
    icon_color  — "primary" (default) | "success" | "warning" | "danger" | "info"
    trend       — int|float (opcional): positivo=↑verde, negativo=↓rojo, 0=→gris
    trend_label — string (opcional): texto junto al trend
    href        — string (opcional): convierte la card en enlace

  Uso simple:
    {% component "unfold/components/stat_card.html"
       with title=_("Pendientes") value=48 icon="inbox" %}
    {% endcomponent %}

  Uso con trend:
    {% component "unfold/components/stat_card.html"
       with title=_("Usuarios activos") value="1,234" icon="group"
            trend=12 trend_label=_("vs mes anterior") %}
    {% endcomponent %}
#}
{% load i18n %}

{% with icon=icon|default:"analytics" icon_color=icon_color|default:"primary" %}

{% if href %}<a href="{{ href }}" class="block group">{% endif %}

<div class="bg-white dark:bg-base-900 border border-base-200 dark:border-base-700 rounded-default p-5
            {% if href %}hover:border-primary-300 dark:hover:border-primary-700 transition-colors{% endif %}">
  <div class="flex items-start justify-between gap-4">
    <div class="flex-1 min-w-0">
      <p class="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400 mb-2">
        {{ title }}
      </p>
      <p class="text-3xl font-bold text-gray-900 dark:text-white leading-none">
        {{ value }}
      </p>
      {% if trend is not None %}
        <div class="flex items-center gap-1.5 mt-2">
          {% if trend > 0 %}
            <span class="text-green-600 dark:text-green-400 text-sm font-semibold">
              <span class="material-symbols-outlined text-sm leading-none align-middle">trending_up</span>
              +{{ trend }}%
            </span>
          {% elif trend < 0 %}
            <span class="text-red-500 dark:text-red-400 text-sm font-semibold">
              <span class="material-symbols-outlined text-sm leading-none align-middle">trending_down</span>
              {{ trend }}%
            </span>
          {% else %}
            <span class="text-gray-500 dark:text-gray-400 text-sm font-semibold">
              <span class="material-symbols-outlined text-sm leading-none align-middle">trending_flat</span>
              0%
            </span>
          {% endif %}
          {% if trend_label %}
            <span class="text-xs text-gray-400 dark:text-gray-500">{{ trend_label }}</span>
          {% endif %}
        </div>
      {% endif %}
    </div>

    <div class="flex-shrink-0 w-11 h-11 rounded-default flex items-center justify-center
      {% if icon_color == 'success' %}bg-green-100 dark:bg-green-900/30
      {% elif icon_color == 'warning' %}bg-yellow-100 dark:bg-yellow-900/30
      {% elif icon_color == 'danger' %}bg-red-100 dark:bg-red-900/30
      {% elif icon_color == 'info' %}bg-blue-100 dark:bg-blue-900/30
      {% else %}bg-primary-100 dark:bg-primary-900/30{% endif %}">
      <span class="material-symbols-outlined text-xl
        {% if icon_color == 'success' %}text-green-600 dark:text-green-400
        {% elif icon_color == 'warning' %}text-yellow-600 dark:text-yellow-400
        {% elif icon_color == 'danger' %}text-red-600 dark:text-red-400
        {% elif icon_color == 'info' %}text-blue-600 dark:text-blue-400
        {% else %}text-primary-600 dark:text-primary-400{% endif %}">
        {{ icon }}
      </span>
    </div>
  </div>
</div>

{% if href %}</a>{% endif %}

{% endwith %}
```

- [ ] **Step 2: Verificar modo simple**

```django
{% load unfold %}
<div style="display:grid;grid-template-columns:repeat(3,1fr);gap:1.5rem">
  {% component "unfold/components/stat_card.html"
     with title=_("Pendientes") value=48 icon="inbox" %}
  {% endcomponent %}
  {% component "unfold/components/stat_card.html"
     with title=_("Completados") value=312 icon="check_circle" icon_color="success" %}
  {% endcomponent %}
  {% component "unfold/components/stat_card.html"
     with title=_("Errores") value=3 icon="cancel" icon_color="danger" %}
  {% endcomponent %}
</div>
```

Verificar: 3 cards en grid, íconos con color semántico, sin trend.

- [ ] **Step 3: Verificar con trend**

```django
{% load unfold %}
<div style="display:grid;grid-template-columns:repeat(2,1fr);gap:1.5rem">
  {% component "unfold/components/stat_card.html"
     with title=_("Usuarios activos") value="1,234" icon="group"
          trend=12 trend_label=_("vs mes anterior") %}
  {% endcomponent %}
  {% component "unfold/components/stat_card.html"
     with title=_("Cancelaciones") value=23 icon="cancel" icon_color="danger"
          trend=-5 trend_label=_("vs mes anterior") %}
  {% endcomponent %}
</div>
```

Verificar: trend positivo verde con ↑, trend negativo rojo con ↓.

- [ ] **Step 4: Commit**

```bash
git add templates/unfold/components/stat_card.html
git commit -m "feat(ui): add StatCard component — trend ↑↓ opcional, 5 colores semánticos, href opcional"
```

---

## Task 4: Inline Edit — `inline_edit.html`

**Files:**
- Create: `templates/unfold/components/inline_edit.html`

- [ ] **Step 1: Crear `inline_edit.html`**

```django
{# templates/unfold/components/inline_edit.html #}
{#
  Edición inline de un campo via HTMX PATCH + Alpine para estado local.

  Parámetros:
    value       — string (requerido): valor actual
    field       — string (requerido): nombre del campo en el modelo
    url         — string (requerido): URL que recibe el PATCH
    field_type  — "text" (default) | "select" | "textarea"
    choices     — list de [value, label] (solo field_type="select")
    placeholder — string (opcional)
    empty_text  — string (default: "—"): texto si value es vacío

  Uso texto:
    {% component "unfold/components/inline_edit.html"
       with value=obj.nombre field="nombre" url=patch_url %}
    {% endcomponent %}

  Uso select:
    {% component "unfold/components/inline_edit.html"
       with value=obj.estado field="estado" url=patch_url
            field_type="select" choices=estado_choices %}
    {% endcomponent %}

  Vista PATCH Django:
    @require_http_methods(["PATCH"])
    def mi_patch_view(request, pk):
        import json
        obj = get_object_or_404(MiModelo, pk=pk)
        data = json.loads(request.body)
        field = data.get("field")
        value = data.get("value")
        allowed = {"nombre", "estado", "descripcion"}
        if field not in allowed:
            return HttpResponse(status=400)
        setattr(obj, field, value)
        obj.save(update_fields=[field])
        return render(request, "unfold/components/inline_edit.html", {
            "value": getattr(obj, field),
            "field": field,
            "url": request.path,
            "field_type": data.get("field_type", "text"),
        })
#}
{% load i18n %}

{% with field_type=field_type|default:"text" empty_text=empty_text|default:"—" %}

<div
  x-data="{
    editing: false,
    saving: false,
    error: false,
    original: '{{ value|escapejs }}',
    current: '{{ value|escapejs }}',
    startEdit() { this.editing = true; this.error = false; this.$nextTick(() => this.$refs.input && this.$refs.input.focus()); },
    cancel() { this.editing = false; this.current = this.original; this.error = false; },
    async save() {
      this.saving = true;
      this.error = false;
      try {
        const res = await fetch('{{ url }}', {
          method: 'PATCH',
          headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.cookie.match(/csrftoken=([^;]+)/)?.[1] || ''
          },
          body: JSON.stringify({ field: '{{ field|escapejs }}', value: this.current, field_type: '{{ field_type }}' })
        });
        if (!res.ok) { this.error = true; this.saving = false; return; }
        const html = await res.text();
        this.$el.outerHTML = html;
      } catch(e) { this.error = true; this.saving = false; }
    }
  }"
  x-on:keydown.escape.window="if(editing) cancel()"
  class="inline-flex items-center gap-1 group"
>
  {# Vista reposo #}
  <span
    x-show="!editing"
    x-on:click="startEdit()"
    class="text-sm text-gray-900 dark:text-white cursor-pointer rounded px-1 -mx-1
           hover:bg-base-100 dark:hover:bg-base-800 transition-colors"
  >
    <span x-text="current || '{{ empty_text }}'"></span>
    <span class="material-symbols-outlined text-xs text-gray-400 opacity-0 group-hover:opacity-100 transition-opacity ml-0.5 align-middle">edit</span>
  </span>

  {# Vista edición #}
  <span x-show="!editing" style="display:none"></span>
  <div x-show="editing" x-cloak class="flex items-center gap-1.5">

    {% if field_type == "select" %}
      <select
        x-ref="input"
        x-model="current"
        class="border rounded-default px-2 py-1 text-sm bg-white dark:bg-base-800 text-gray-900 dark:text-white
               focus:outline-none focus:ring-2 focus:ring-primary-500
               {% if error %}border-red-500{% else %}border-primary-400{% endif %}"
      >
        {% for choice_value, choice_label in choices %}
          <option value="{{ choice_value }}" {% if choice_value == value %}selected{% endif %}>{{ choice_label }}</option>
        {% endfor %}
      </select>

    {% elif field_type == "textarea" %}
      <textarea
        x-ref="input"
        x-model="current"
        rows="3"
        placeholder="{{ placeholder }}"
        class="border rounded-default px-2 py-1 text-sm bg-white dark:bg-base-800 text-gray-900 dark:text-white
               focus:outline-none focus:ring-2 focus:ring-primary-500 resize-none min-w-[200px]
               {% if error %}border-red-500{% else %}border-primary-400{% endif %}"
      ></textarea>

    {% else %}
      <input
        type="text"
        x-ref="input"
        x-model="current"
        placeholder="{{ placeholder }}"
        x-on:keydown.enter="save()"
        class="border rounded-default px-2 py-1 text-sm bg-white dark:bg-base-800 text-gray-900 dark:text-white
               focus:outline-none focus:ring-2 focus:ring-primary-500
               {% if error %}border-red-500{% else %}border-primary-400{% endif %}"
      >
    {% endif %}

    {# Botón guardar #}
    <button
      type="button"
      x-on:click="save()"
      :disabled="saving"
      class="p-1 rounded text-green-600 hover:bg-green-50 dark:hover:bg-green-900/20 transition-colors disabled:opacity-50"
      aria-label="{% trans 'Guardar' %}"
    >
      <span class="material-symbols-outlined text-base leading-none" x-text="saving ? 'progress_activity' : 'check'"></span>
    </button>

    {# Botón cancelar #}
    <button
      type="button"
      x-on:click="cancel()"
      class="p-1 rounded text-gray-400 hover:bg-base-100 dark:hover:bg-base-800 transition-colors"
      aria-label="{% trans 'Cancelar' %}"
    >
      <span class="material-symbols-outlined text-base leading-none">close</span>
    </button>

    {# Error #}
    <span x-show="error" class="text-xs text-red-500">
      {% trans "Error al guardar" %}
    </span>

  </div>
</div>

{% endwith %}
```

- [ ] **Step 2: Verificar modo texto en browser**

Crear una vista PATCH temporal en `apps/core/views.py` para probar:

```python
import json
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
from django.views.decorators.http import require_http_methods

User = get_user_model()

@login_required
@require_http_methods(["PATCH"])
def user_inline_patch(request, pk):
    obj = get_object_or_404(User, pk=pk)
    data = json.loads(request.body)
    field = data.get("field")
    value = data.get("value")
    allowed = {"first_name", "last_name"}
    if field not in allowed:
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

Agregar URL en `apps/core/urls.py`:
```python
path("user/<int:pk>/patch/", user_inline_patch, name="user_inline_patch"),
```

En un template de prueba:
```django
{% load unfold %}
{% component "unfold/components/inline_edit.html"
   with value=user.first_name field="first_name" url=patch_url %}
{% endcomponent %}
```

Verificar: valor visible con lápiz al hover → click abre input → Enter guarda → el componente se re-renderiza con el nuevo valor. Escape cancela sin request.

- [ ] **Step 3: Verificar modo select**

```python
estado_choices = [("active", "Activo"), ("inactive", "Inactivo"), ("pending", "Pendiente")]
context["estado_choices"] = estado_choices
```

```django
{% load unfold %}
{% component "unfold/components/inline_edit.html"
   with value="active" field="estado" url="/test/patch/"
        field_type="select" choices=estado_choices %}
{% endcomponent %}
```

Verificar: click abre dropdown con las 3 opciones, seleccionar y guardar con ✓.

- [ ] **Step 4: Commit**

```bash
git add templates/unfold/components/inline_edit.html
git commit -m "feat(ui): add InlineEdit component — text/select/textarea, HTMX PATCH, Alpine state"
```

---

## Self-review

- [x] `page_header.html` — `{{ component_content }}` es el slot de acciones — si está vacío no renderiza el div
- [x] `filter_tabs.html` — `hx-trigger="load"` dispara automáticamente sin JS extra
- [x] `stat_card.html` — `{% if trend is not None %}` permite pasar `trend=0` como valor válido
- [x] `inline_edit.html` — CSRF token leído de cookie, compatible con Django sin configuración extra
- [x] `inline_edit.html` — `x-cloak` requiere `[x-cloak] { display: none }` en CSS — Unfold ya incluye esta regla
- [x] `inline_edit.html` — `outerHTML` reemplaza el componente completo, incluyendo el `x-data` fresh — no hay estado residual
- [x] Ningún componente requiere migraciones
