# Empty State + Loading Skeleton Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Crear 2 componentes de feedback — `empty_state.html` y `skeleton.html` — en `templates/unfold/components/` siguiendo la convención del proyecto.

**Architecture:** Ambos son templates puros Django sin JS. `empty_state.html` usa Material Symbols (`<span class="material-symbols-outlined">`) para íconos. `skeleton.html` define su animación shimmer con `<style>` inline para no depender de CSS externo. Ninguno requiere vistas ni URLs nuevas.

**Tech Stack:** Django templates, Tailwind CSS (clases Unfold), Material Symbols (ya incluido en Unfold).

---

## Mapa de archivos

| Acción | Archivo |
|--------|---------|
| Crear | `templates/unfold/components/empty_state.html` |
| Crear | `templates/unfold/components/skeleton.html` |

---

## Task 1: Empty State — `empty_state.html`

**Files:**
- Create: `templates/unfold/components/empty_state.html`

- [ ] **Step 1: Crear `empty_state.html`**

```django
{# templates/unfold/components/empty_state.html #}
{#
  Estado vacío reutilizable para listas, tablas y secciones sin datos.

  Parámetros:
    icon         — string Material Symbol (default: "inbox")
    title        — string (requerido)
    subtitle     — string (opcional)
    action_label — string (opcional) — texto del botón
    action_url   — string (opcional) — URL del botón
    class        — string (opcional) — clases extra para el contenedor

  Uso sin acción:
    {% component "unfold/components/empty_state.html"
       with icon="inbox" title=_("Sin registros") subtitle=_("Aún no hay datos.") %}
    {% endcomponent %}

  Uso con acción:
    {% component "unfold/components/empty_state.html"
       with icon="group" title=_("Sin usuarios")
            action_label=_("Crear usuario") action_url="/admin/core/user/add/" %}
    {% endcomponent %}
#}
{% load i18n %}

{% with icon=icon|default:"inbox" %}
<div class="flex flex-col items-center justify-center py-12 px-6 text-center {{ class }}">

  <span class="material-symbols-outlined text-5xl text-gray-300 dark:text-gray-600 mb-4">
    {{ icon }}
  </span>

  <p class="text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1">
    {{ title }}
  </p>

  {% if subtitle %}
    <p class="text-xs text-gray-400 dark:text-gray-500 mb-4">
      {{ subtitle }}
    </p>
  {% endif %}

  {% if action_label and action_url %}
    <a
      href="{{ action_url }}"
      class="inline-flex items-center gap-1.5 px-4 py-2 text-xs font-medium rounded-default
             bg-primary-600 hover:bg-primary-700 text-white transition-colors mt-2"
    >
      <span class="material-symbols-outlined text-sm leading-none">add</span>
      {{ action_label }}
    </a>
  {% endif %}

</div>
{% endwith %}
```

- [ ] **Step 2: Verificar en browser — modo sin acción**

En cualquier template de prueba dentro del admin:

```django
{% load unfold %}
{% component "unfold/components/card.html" with title=_("Usuarios") %}
  {% component "unfold/components/empty_state.html"
     with icon="group"
          title=_("Sin usuarios")
          subtitle=_("Aún no se han creado usuarios.") %}
  {% endcomponent %}
{% endcomponent %}
```

Verificar: ícono `group` centrado y tenue, título, subtítulo. Sin botón.

- [ ] **Step 3: Verificar en browser — modo con acción**

```django
{% load unfold %}
{% component "unfold/components/card.html" with title=_("Usuarios") %}
  {% component "unfold/components/empty_state.html"
     with icon="group"
          title=_("Sin usuarios")
          subtitle=_("Comienza creando el primero.")
          action_label=_("Crear usuario")
          action_url="/admin/core/user/add/" %}
  {% endcomponent %}
{% endcomponent %}
```

Verificar: aparece botón azul "Crear usuario" con ícono `add`. Click navega a `/admin/core/user/add/`.

- [ ] **Step 4: Commit**

```bash
git add templates/unfold/components/empty_state.html
git commit -m "feat(ui): add EmptyState component — ícono Material Symbols, acción opcional"
```

---

## Task 2: Loading Skeleton — `skeleton.html`

**Files:**
- Create: `templates/unfold/components/skeleton.html`

- [ ] **Step 1: Crear `skeleton.html`**

```django
{# templates/unfold/components/skeleton.html #}
{#
  Placeholder animado (shimmer) para contenido que carga de forma async.

  Parámetros:
    type   — "lines" (default) | "table"
    rows   — int (default: 3) — número de filas
    cols   — int (default: 4) — columnas en modo "table"
    avatar — bool (default: True) — círculo avatar en modo "lines"

  Uso lines (default):
    {% component "unfold/components/skeleton.html" with rows=3 %}{% endcomponent %}

  Uso table:
    {% component "unfold/components/skeleton.html" with rows=5 type="table" cols=4 %}{% endcomponent %}

  Uso lines sin avatar:
    {% component "unfold/components/skeleton.html" with rows=4 avatar=False %}{% endcomponent %}

  Patrón HTMX — mostrar skeleton mientras carga:
    <div id="mi-lista"
         hx-get="{% url 'mi_vista' %}"
         hx-trigger="load"
         hx-swap="innerHTML">
      {% component "unfold/components/skeleton.html" with rows=5 type="table" cols=3 %}{% endcomponent %}
    </div>
#}
{% load i18n %}

{% with type=type|default:"lines" rows=rows|default:3 cols=cols|default:4 %}

<style>
  @keyframes sk-shimmer {
    0%   { background-position: -200% 0; }
    100% { background-position:  200% 0; }
  }
  .sk-bar {
    background: linear-gradient(
      90deg,
      rgb(var(--color-base-100, 241 245 249)) 25%,
      rgb(var(--color-base-200, 226 232 240)) 50%,
      rgb(var(--color-base-100, 241 245 249)) 75%
    );
    background-size: 200% 100%;
    animation: sk-shimmer 1.5s ease-in-out infinite;
    border-radius: 4px;
  }
  .dark .sk-bar {
    background: linear-gradient(
      90deg,
      rgb(var(--color-base-800, 30 41 59)) 25%,
      rgb(var(--color-base-700, 51 65 85)) 50%,
      rgb(var(--color-base-800, 30 41 59)) 75%
    );
    background-size: 200% 100%;
  }
</style>

{% if type == "table" %}
  {# ── Tabla skeleton ── #}
  <div class="w-full overflow-hidden">
    {# Cabecera #}
    <div class="flex gap-4 px-4 py-3 bg-base-50 dark:bg-base-800/50 border-b border-base-200 dark:border-base-700">
      {% for i in cols|make_list %}
        <div class="sk-bar h-3 flex-1" style="max-width:{% cycle '80px' '140px' '60px' '100px' %}"></div>
      {% endfor %}
    </div>
    {# Filas #}
    {% for i in rows|make_list %}
      <div class="flex gap-4 items-center px-4 py-3 border-b border-base-100 dark:border-base-800">
        {% for j in cols|make_list %}
          <div class="sk-bar h-3 flex-1"
               style="max-width:{% cycle '90px' '150px' '50px' '110px' %};opacity:{% cycle '1' '.85' '.7' '.9' %}">
          </div>
        {% endfor %}
      </div>
    {% endfor %}
  </div>

{% else %}
  {# ── Lines skeleton (default) ── #}
  <div class="flex flex-col gap-4 p-1">
    {% for i in rows|make_list %}
      <div class="flex items-center gap-3">
        {% if avatar != False %}
          <div class="sk-bar rounded-full flex-shrink-0" style="width:36px;height:36px"></div>
        {% endif %}
        <div class="flex flex-col gap-2 flex-1">
          <div class="sk-bar h-3" style="width:{% cycle '60%' '75%' '50%' '65%' %}"></div>
          <div class="sk-bar h-2.5" style="width:{% cycle '40%' '55%' '35%' '45%' %}"></div>
        </div>
      </div>
    {% endfor %}
  </div>
{% endif %}

{% endwith %}
```

- [ ] **Step 2: Verificar modo lines en browser**

```django
{% load unfold %}
{% component "unfold/components/card.html" with title=_("Cargando...") %}
  {% component "unfold/components/skeleton.html" with rows=4 %}{% endcomponent %}
{% endcomponent %}
```

Verificar: 4 filas con círculo avatar + 2 barras de texto por fila, animación shimmer activa.

- [ ] **Step 3: Verificar modo table en browser**

```django
{% load unfold %}
{% component "unfold/components/card.html" with title=_("Cargando tabla...") %}
  {% component "unfold/components/skeleton.html" with rows=5 type="table" cols=3 %}{% endcomponent %}
{% endcomponent %}
```

Verificar: cabecera con 3 columnas + 5 filas con 3 columnas cada una, animación shimmer activa.

- [ ] **Step 4: Verificar modo lines sin avatar**

```django
{% load unfold %}
{% component "unfold/components/skeleton.html" with rows=3 avatar=False %}{% endcomponent %}
```

Verificar: 3 filas de barras de texto, sin círculo avatar.

- [ ] **Step 5: Commit**

```bash
git add templates/unfold/components/skeleton.html
git commit -m "feat(ui): add Skeleton component — lines y table mode, shimmer animation, configurable rows/cols"
```

---

## Self-review

- [x] `empty_state.html` — botón solo aparece si AMBOS `action_label` y `action_url` están presentes
- [x] `empty_state.html` — `icon|default:"inbox"` evita error si no se pasa ícono
- [x] `skeleton.html` — `@keyframes` inline para no depender de CSS externo
- [x] `skeleton.html` — colores shimmer usan variables CSS de Unfold con fallback para dark mode
- [x] `skeleton.html` — `rows|make_list` y `cols|make_list` usan el filtro de Django para iterar N veces desde un int
- [x] Ningún componente requiere vistas, URLs ni migraciones nuevas
