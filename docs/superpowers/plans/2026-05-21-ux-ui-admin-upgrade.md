# UX/UI Admin Upgrade Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Mejorar la UX/UI genérica del template admin con htmx polling para notificaciones in-app, dashboard con widgets de ejemplo, y mejoras Unfold nativas en todos los ModelAdmin existentes.

**Architecture:** Unfold 0.40 como base UI; django-htmx para polling de notificaciones sin JS manual; Chart.js CDN cargado solo en el dashboard. Las notificaciones in-app usan el modelo `Notification` existente con tres endpoints nuevos en `apps/notifications/`. El dashboard usa `UNFOLD["DASHBOARD_CALLBACK"]` apuntando a `apps/core/dashboard.py`.

**Tech Stack:** Django 6, Unfold 0.40, django-htmx>=1.17, htmx CDN, Chart.js CDN

---

## Task 1: Instalar django-htmx y configurar middleware

**Files:**
- Modify: `requirements/base.txt`
- Modify: `config/settings/base.py`

- [ ] **Step 1: Agregar django-htmx a requirements**

Editar `requirements/base.txt` para que quede:
```
Django>=6.0,<6.1
psycopg2-binary>=2.9
python-dotenv>=1.0
django-unfold>=0.40
mysqlclient>=2.2
gunicorn>=21.0
requests>=2.31
django-htmx>=1.17
```

- [ ] **Step 2: Agregar django_htmx a DJANGO_APPS en settings**

En `config/settings/base.py`, la lista `DJANGO_APPS` debe quedar:
```python
DJANGO_APPS = [
    "unfold",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django_htmx",
]
```

- [ ] **Step 3: Agregar HtmxMiddleware a MIDDLEWARE**

En `config/settings/base.py`, agregar `"django_htmx.middleware.HtmxMiddleware"` justo después de `SecurityMiddleware`. La lista `MIDDLEWARE` debe comenzar:
```python
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    ...
]
```

- [ ] **Step 4: Instalar la dependencia en el contenedor**

```bash
make down && make up
```

Verificar que el servidor arranca sin `ModuleNotFoundError: No module named 'django_htmx'`.

- [ ] **Step 5: Commit**

```bash
git add requirements/base.txt config/settings/base.py
git commit -m "feat: add django-htmx dependency and middleware"
```

---

## Task 2: Endpoints htmx para notificaciones in-app

**Files:**
- Create: `apps/notifications/views.py`
- Create: `apps/notifications/urls.py`
- Modify: `config/urls.py`

- [ ] **Step 1: Escribir los tests que fallan**

Crear `apps/notifications/tests_views.py`:
```python
from django.contrib.auth import get_user_model
from django.test import TestCase, RequestFactory
from django.utils import timezone

User = get_user_model()


class NotificationViewsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="viewuser", password="pass")
        self.client.login(username="viewuser", password="pass")

    def _htmx_get(self, url):
        return self.client.get(url, HTTP_HX_REQUEST="true")

    def _htmx_post(self, url):
        return self.client.post(url, HTTP_HX_REQUEST="true")

    def test_unread_count_requires_login(self):
        self.client.logout()
        response = self.client.get("/admin/notifications/unread-count/", HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 302)

    def test_unread_count_returns_200(self):
        response = self._htmx_get("/admin/notifications/unread-count/")
        self.assertEqual(response.status_code, 200)

    def test_unread_count_shows_zero_when_no_notifications(self):
        response = self._htmx_get("/admin/notifications/unread-count/")
        self.assertContains(response, "0")

    def test_unread_count_shows_correct_number(self):
        from apps.notifications.models import Notification
        Notification.objects.create(
            recipient=self.user,
            title="Test",
            body="Body",
            channel="in_app",
        )
        response = self._htmx_get("/admin/notifications/unread-count/")
        self.assertContains(response, "1")

    def test_unread_list_returns_200(self):
        response = self._htmx_get("/admin/notifications/unread-list/")
        self.assertEqual(response.status_code, 200)

    def test_unread_list_shows_notification_title(self):
        from apps.notifications.models import Notification
        Notification.objects.create(
            recipient=self.user,
            title="Mi notificacion",
            body="Body",
            channel="in_app",
        )
        response = self._htmx_get("/admin/notifications/unread-list/")
        self.assertContains(response, "Mi notificacion")

    def test_mark_read_marks_all_as_read(self):
        from apps.notifications.models import Notification
        Notification.objects.create(
            recipient=self.user, title="A", body="B", channel="in_app"
        )
        self._htmx_post("/admin/notifications/mark-read/")
        self.assertEqual(
            Notification.objects.filter(recipient=self.user, read_at__isnull=True).count(),
            0,
        )

    def test_mark_read_returns_badge_with_zero(self):
        response = self._htmx_post("/admin/notifications/mark-read/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "0")
```

- [ ] **Step 2: Ejecutar tests — deben fallar con 404**

```bash
make test
```
Esperado: FAIL — `404` porque las URLs no existen aún.

- [ ] **Step 3: Crear las vistas en `apps/notifications/views.py`**

```python
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from .models import Notification


def _require_htmx(request):
    if not request.htmx:
        return HttpResponseForbidden()
    return None


@login_required
@require_GET
def unread_count_view(request):
    if err := _require_htmx(request):
        return err
    count = Notification.objects.filter(
        recipient=request.user,
        channel=Notification.Channel.IN_APP,
        read_at__isnull=True,
    ).count()
    return render(request, "partials/notifications_badge.html", {"count": count})


@login_required
@require_GET
def unread_list_view(request):
    if err := _require_htmx(request):
        return err
    notifications = Notification.objects.filter(
        recipient=request.user,
        channel=Notification.Channel.IN_APP,
        read_at__isnull=True,
    ).order_by("-created_at")[:10]
    return render(request, "partials/notifications_list.html", {"notifications": notifications})


@login_required
@require_POST
def mark_read_view(request):
    if err := _require_htmx(request):
        return err
    Notification.objects.filter(
        recipient=request.user,
        channel=Notification.Channel.IN_APP,
        read_at__isnull=True,
    ).update(read_at=timezone.now())
    return render(request, "partials/notifications_badge.html", {"count": 0})
```

- [ ] **Step 4: Crear `apps/notifications/urls.py`**

```python
from django.urls import path
from . import views

urlpatterns = [
    path("unread-count/", views.unread_count_view, name="notifications_unread_count"),
    path("unread-list/", views.unread_list_view, name="notifications_unread_list"),
    path("mark-read/", views.mark_read_view, name="notifications_mark_read"),
]
```

- [ ] **Step 5: Registrar URLs en `config/urls.py`**

```python
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path

from apps.core.forms import PlatformAuthenticationForm
from apps.core.views import solicitar_acceso

admin.site.login_form = PlatformAuthenticationForm

urlpatterns = [
    path("i18n/", include("django.conf.urls.i18n")),
    path("admin/password_reset/", auth_views.PasswordResetView.as_view(), name="admin_password_reset"),
    path("admin/password_reset/done/", auth_views.PasswordResetDoneView.as_view(), name="password_reset_done"),
    path("reset/<uidb64>/<token>/", auth_views.PasswordResetConfirmView.as_view(), name="password_reset_confirm"),
    path("reset/done/", auth_views.PasswordResetCompleteView.as_view(), name="password_reset_complete"),
    path("admin/", admin.site.urls),
    path("admin/notifications/", include("apps.notifications.urls")),
    path("solicitar-acceso/", solicitar_acceso, name="request_access"),
    # Agregar URLs específicas del proyecto aquí
]
```

- [ ] **Step 6: Crear los templates parciales**

Crear `templates/partials/notifications_badge.html`:
```html
<span id="notifications-badge"
      hx-get="{% url 'notifications_unread_count' %}"
      hx-trigger="every 30s"
      hx-swap="outerHTML"
      class="relative inline-flex items-center">
  <span class="material-symbols-outlined text-2xl leading-none">notifications</span>
  {% if count > 0 %}
  <span class="absolute -top-1 -right-1 flex h-4 w-4 items-center justify-center rounded-full bg-red-500 text-[10px] font-bold text-white leading-none">
    {{ count }}
  </span>
  {% endif %}
</span>
```

Crear `templates/partials/notifications_list.html`:
```html
<div id="notifications-dropdown"
     class="absolute right-0 mt-2 w-80 rounded-lg shadow-lg bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 z-50">
  <div class="p-3 border-b border-gray-200 dark:border-gray-700">
    <span class="text-sm font-semibold text-gray-700 dark:text-gray-200">{% trans "Notificaciones" %}</span>
  </div>
  <ul class="max-h-72 overflow-y-auto divide-y divide-gray-100 dark:divide-gray-700">
    {% for n in notifications %}
    <li class="p-3 hover:bg-gray-50 dark:hover:bg-gray-700">
      <p class="text-sm font-medium text-gray-800 dark:text-gray-100 truncate">{{ n.title }}</p>
      <p class="text-xs text-gray-500 dark:text-gray-400 mt-0.5 truncate">{{ n.body|truncatechars:60 }}</p>
      <p class="text-xs text-gray-400 dark:text-gray-500 mt-0.5">{{ n.created_at|timesince }} {% trans "atrás" %}</p>
    </li>
    {% empty %}
    <li class="p-4 text-sm text-center text-gray-400 dark:text-gray-500">{% trans "Sin notificaciones nuevas" %}</li>
    {% endfor %}
  </ul>
  <div class="p-2 border-t border-gray-200 dark:border-gray-700">
    <a href="{% url 'admin:notifications_notification_changelist' %}"
       class="block text-center text-xs text-blue-600 dark:text-blue-400 hover:underline py-1">
      {% trans "Ver todas" %}
    </a>
  </div>
</div>
```

- [ ] **Step 7: Ejecutar tests — deben pasar**

```bash
make test
```
Esperado: PASS en todos los tests de `tests_views.py`.

- [ ] **Step 8: Commit**

```bash
git add apps/notifications/views.py apps/notifications/urls.py apps/notifications/tests_views.py config/urls.py templates/partials/notifications_badge.html templates/partials/notifications_list.html
git commit -m "feat: htmx endpoints for in-app notifications (unread count, list, mark read)"
```

---

## Task 3: Bell icon en el header del admin

**Files:**
- Create: `templates/admin/base_site.html`
- Create: `templates/partials/notifications_bell.html`

- [ ] **Step 1: Crear el template del bell (wrapper con toggle htmx)**

Crear `templates/partials/notifications_bell.html`:
```html
{% load i18n %}
<div class="relative flex items-center"
     x-data="{ open: false }"
     @click.outside="open = false">

  <button @click="open = !open"
          hx-get="{% url 'notifications_unread_list' %}"
          hx-target="#notifications-dropdown-container"
          hx-swap="innerHTML"
          hx-trigger="click"
          hx-on::after-request="
            fetch('{% url 'notifications_mark_read' %}', {method:'POST', headers:{'X-CSRFToken':'{{ csrf_token }}','HX-Request':'true'}})
              .then(() => htmx.trigger('#notifications-badge', 'htmx:trigger'));
          "
          class="relative flex items-center justify-center w-9 h-9 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
          aria-label="{% trans 'Notificaciones' %}">
    {% include "partials/notifications_badge.html" %}
  </button>

  <div id="notifications-dropdown-container"
       x-show="open"
       x-cloak
       class="absolute right-0 top-10">
  </div>
</div>
```

- [ ] **Step 2: Crear `templates/admin/base_site.html` con htmx CDN y bell**

Unfold expone el bloque `{% block topbar_right %}` para inyectar elementos en el header derecho.

```html
{% extends "unfold/base_site.html" %}
{% load i18n %}

{% block extrahead %}
  {{ block.super }}
  <script src="https://unpkg.com/htmx.org@2.0.4" integrity="sha384-HGfztofotfshcF7+8n44JQL2oJmowVChPTg48S+jvZoztPfvwD79OC/LTtG6dMp+" crossorigin="anonymous"></script>
{% endblock %}

{% block topbar_right %}
  {% if request.user.is_authenticated %}
    {% include "partials/notifications_bell.html" %}
  {% endif %}
  {{ block.super }}
{% endblock %}
```

- [ ] **Step 3: Verificar manualmente en el browser**

```bash
make up
```

Ir a `http://localhost:8000/admin/` — verificar que:
1. El bell icon aparece en el header derecho
2. Haciendo click aparece el dropdown de notificaciones
3. La consola del browser no muestra errores JS

- [ ] **Step 4: Commit**

```bash
git add templates/admin/base_site.html templates/partials/notifications_bell.html
git commit -m "feat: notification bell icon in admin header with htmx polling"
```

---

## Task 4: Dashboard de inicio con widgets

**Files:**
- Create: `apps/core/dashboard.py`
- Modify: `config/settings/base.py`
- Create: `templates/admin/dashboard.html`
- Create: `templates/partials/dashboard_card.html`
- Create: `templates/partials/dashboard_chart.html`

- [ ] **Step 1: Escribir el test para dashboard_callback**

Crear `apps/core/tests_dashboard.py`:
```python
from django.contrib.auth import get_user_model
from django.test import TestCase, RequestFactory

User = get_user_model()


class DashboardCallbackTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="dashuser", password="pass")
        self.factory = RequestFactory()

    def test_dashboard_callback_returns_context_with_stat_cards(self):
        from apps.core.dashboard import dashboard_callback
        request = self.factory.get("/admin/")
        request.user = self.user
        context = {}
        result = dashboard_callback(request, context)
        self.assertIn("stat_cards", result)
        self.assertIsInstance(result["stat_cards"], list)
        self.assertGreater(len(result["stat_cards"]), 0)

    def test_dashboard_callback_stat_cards_have_required_keys(self):
        from apps.core.dashboard import dashboard_callback
        request = self.factory.get("/admin/")
        request.user = self.user
        context = {}
        result = dashboard_callback(request, context)
        for card in result["stat_cards"]:
            self.assertIn("title", card)
            self.assertIn("value", card)
            self.assertIn("icon", card)

    def test_dashboard_callback_returns_context_with_recent_users(self):
        from apps.core.dashboard import dashboard_callback
        request = self.factory.get("/admin/")
        request.user = self.user
        context = {}
        result = dashboard_callback(request, context)
        self.assertIn("recent_users", result)

    def test_dashboard_callback_returns_context_with_recent_audit(self):
        from apps.core.dashboard import dashboard_callback
        request = self.factory.get("/admin/")
        request.user = self.user
        context = {}
        result = dashboard_callback(request, context)
        self.assertIn("recent_audit", result)
```

- [ ] **Step 2: Ejecutar test — debe fallar con ImportError**

```bash
make test
```
Esperado: FAIL — `ModuleNotFoundError: No module named 'apps.core.dashboard'`

- [ ] **Step 3: Crear `apps/core/dashboard.py`**

```python
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

User = get_user_model()


def dashboard_callback(request, context):
    """
    Inyecta datos de widgets en el contexto del dashboard de Unfold.

    PROYECTO: Para personalizar, copia esta función a tu app y actualiza
    UNFOLD["DASHBOARD_CALLBACK"] en config/settings/base.py para apuntar a ella.
    Agrega las claves que necesites a context.update({...}).
    """
    from apps.audit.models import AuditLog
    from apps.notifications.models import Notification

    today = timezone.now().date()

    total_users = User.objects.count()
    unread_notifications = Notification.objects.filter(
        recipient=request.user,
        channel="in_app",
        read_at__isnull=True,
    ).count()
    audit_today = AuditLog.objects.filter(timestamp__date=today).count()

    context.update({
        "stat_cards": [
            {
                "title": _("Usuarios"),
                "value": total_users,
                "icon": "group",
                "description": _("Total registrados"),
            },
            {
                "title": _("Notificaciones"),
                "value": unread_notifications,
                "icon": "notifications",
                "description": _("Sin leer"),
            },
            {
                "title": _("Auditoría hoy"),
                "value": audit_today,
                "icon": "history",
                "description": _("Registros de hoy"),
            },
        ],
        "recent_users": User.objects.order_by("-date_joined")[:5],
        "recent_audit": AuditLog.objects.order_by("-timestamp")[:5],
    })
    return context
```

- [ ] **Step 4: Ejecutar test — debe pasar**

```bash
make test
```
Esperado: PASS en todos los tests de `tests_dashboard.py`.

- [ ] **Step 5: Configurar DASHBOARD_CALLBACK en settings**

En `config/settings/base.py`, dentro del dict `UNFOLD`, agregar justo después de `"SHOW_LANGUAGES": True,`:
```python
"DASHBOARD_CALLBACK": "apps.core.dashboard.dashboard_callback",
```

- [ ] **Step 6: Crear `templates/partials/dashboard_card.html`**

```html
<div class="flex items-center gap-4 rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 p-5 shadow-sm">
  <div class="flex h-12 w-12 items-center justify-center rounded-full bg-blue-100 dark:bg-blue-900/30 flex-shrink-0">
    <span class="material-symbols-outlined text-blue-600 dark:text-blue-400 text-2xl">{{ card.icon }}</span>
  </div>
  <div>
    <p class="text-2xl font-bold text-gray-900 dark:text-white">{{ card.value }}</p>
    <p class="text-sm font-medium text-gray-500 dark:text-gray-400">{{ card.title }}</p>
    {% if card.description %}
    <p class="text-xs text-gray-400 dark:text-gray-500 mt-0.5">{{ card.description }}</p>
    {% endif %}
  </div>
</div>
```

- [ ] **Step 7: Crear `templates/partials/dashboard_chart.html`**

```html
{% load i18n %}
{# PROYECTO: reemplaza chartData y chartLabels con datos reales de tu app #}
{# Ejemplo: pasa los datos desde dashboard_callback en context["chart_data"] #}
<div class="rounded-lg border border-dashed border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 p-6">
  <div class="flex items-center justify-between mb-4">
    <h3 class="text-sm font-semibold text-gray-700 dark:text-gray-200">
      {% trans "Actividad (ejemplo)" %}
    </h3>
    <span class="text-xs text-gray-400 dark:text-gray-500 bg-yellow-50 dark:bg-yellow-900/20 text-yellow-600 dark:text-yellow-400 px-2 py-0.5 rounded-full">
      {% trans "Placeholder — reemplazar con datos reales" %}
    </span>
  </div>
  <canvas id="dashboardChart" height="80"></canvas>
</div>

<script>
  // PROYECTO: reemplaza estos arrays con datos reales desde el contexto Django
  // Ejemplo: const chartLabels = {{ chart_labels|safe }};
  const chartLabels = ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"];
  const chartData = [12, 19, 8, 15, 22, 6, 10];

  document.addEventListener("DOMContentLoaded", function () {
    const ctx = document.getElementById("dashboardChart").getContext("2d");
    new Chart(ctx, {
      type: "bar",
      data: {
        labels: chartLabels,
        datasets: [{
          label: "Actividad",
          data: chartData,
          backgroundColor: "rgba(59, 130, 246, 0.5)",
          borderColor: "rgba(59, 130, 246, 1)",
          borderWidth: 1,
          borderRadius: 4,
        }]
      },
      options: {
        responsive: true,
        plugins: { legend: { display: false } },
        scales: { y: { beginAtZero: true, ticks: { precision: 0 } } }
      }
    });
  });
</script>
```

- [ ] **Step 8: Crear `templates/admin/dashboard.html`**

```html
{% extends "unfold/layouts/base_simple.html" %}
{% load i18n %}

{% block content %}
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>

<div class="px-4 py-6 space-y-6 lg:px-8">

  {# Stat Cards #}
  <div class="grid grid-cols-1 gap-4 sm:grid-cols-3">
    {% for card in stat_cards %}
      {% include "partials/dashboard_card.html" with card=card %}
    {% endfor %}
  </div>

  {# Chart slot #}
  {% include "partials/dashboard_chart.html" %}

  {# List widgets #}
  <div class="grid grid-cols-1 gap-4 lg:grid-cols-2">

    {# Últimos usuarios #}
    <div class="rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 overflow-hidden">
      <div class="px-4 py-3 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
        <h3 class="text-sm font-semibold text-gray-700 dark:text-gray-200">{% trans "Últimos usuarios" %}</h3>
        <a href="{% url 'admin:core_user_changelist' %}" class="text-xs text-blue-600 dark:text-blue-400 hover:underline">{% trans "Ver todos" %}</a>
      </div>
      <ul class="divide-y divide-gray-100 dark:divide-gray-700">
        {% for user in recent_users %}
        <li class="flex items-center gap-3 px-4 py-3">
          <span class="material-symbols-outlined text-gray-400 text-lg">person</span>
          <div class="min-w-0 flex-1">
            <p class="text-sm font-medium text-gray-800 dark:text-gray-100 truncate">{{ user.username }}</p>
            <p class="text-xs text-gray-400 dark:text-gray-500 truncate">{{ user.email }}</p>
          </div>
          <span class="text-xs text-gray-400 dark:text-gray-500 flex-shrink-0">{{ user.date_joined|date:"d/m/y" }}</span>
        </li>
        {% empty %}
        <li class="px-4 py-4 text-sm text-gray-400 dark:text-gray-500 text-center">{% trans "Sin usuarios" %}</li>
        {% endfor %}
      </ul>
    </div>

    {# Últimas entradas de auditoría #}
    <div class="rounded-lg border border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 overflow-hidden">
      <div class="px-4 py-3 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
        <h3 class="text-sm font-semibold text-gray-700 dark:text-gray-200">{% trans "Auditoría reciente" %}</h3>
        <a href="{% url 'admin:audit_auditlog_changelist' %}" class="text-xs text-blue-600 dark:text-blue-400 hover:underline">{% trans "Ver todas" %}</a>
      </div>
      <ul class="divide-y divide-gray-100 dark:divide-gray-700">
        {% for log in recent_audit %}
        <li class="flex items-center gap-3 px-4 py-3">
          <span class="material-symbols-outlined text-gray-400 text-lg">history</span>
          <div class="min-w-0 flex-1">
            <p class="text-sm font-medium text-gray-800 dark:text-gray-100 truncate">{{ log.model_name }} — {{ log.get_action_display }}</p>
            <p class="text-xs text-gray-400 dark:text-gray-500 truncate">{{ log.object_repr }}</p>
          </div>
          <span class="text-xs text-gray-400 dark:text-gray-500 flex-shrink-0">{{ log.timestamp|date:"d/m H:i" }}</span>
        </li>
        {% empty %}
        <li class="px-4 py-4 text-sm text-gray-400 dark:text-gray-500 text-center">{% trans "Sin registros" %}</li>
        {% endfor %}
      </ul>
    </div>

  </div>
</div>
{% endblock %}
```

- [ ] **Step 9: Verificar dashboard en el browser**

Ir a `http://localhost:8000/admin/` — verificar que:
1. Las 3 stat cards aparecen con valores reales
2. La gráfica de ejemplo se renderiza
3. Las dos listas de usuarios y auditoría aparecen

- [ ] **Step 10: Commit**

```bash
git add apps/core/dashboard.py apps/core/tests_dashboard.py config/settings/base.py templates/admin/dashboard.html templates/partials/dashboard_card.html templates/partials/dashboard_chart.html
git commit -m "feat: admin dashboard with stat cards, chart slot, and recent lists"
```

---

## Task 5: Mejoras Unfold en ModelAdmin existentes

**Files:**
- Modify: `apps/core/admin.py`
- Modify: `apps/audit/admin.py`
- Modify: `apps/notifications/admin.py`
- Modify: `apps/config/admin.py`
- Modify: `apps/permissions/admin.py`

- [ ] **Step 1: Escribir test para bulk action de NotificationAdmin**

Agregar al final de `apps/notifications/tests.py`:
```python
class NotificationAdminBulkActionTest(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            username="admin_bulk", password="pass", email="admin_bulk@example.com"
        )
        self.user = User.objects.create_user(username="target_bulk", password="pass")
        self.client.login(username="admin_bulk", password="pass")

    def test_mark_as_read_action(self):
        from apps.notifications.models import Notification
        n = Notification.objects.create(
            recipient=self.user,
            title="Bulk test",
            body="Body",
            channel="in_app",
        )
        response = self.client.post(
            "/admin/notifications/notification/",
            {
                "action": "mark_as_read",
                "_selected_action": [n.pk],
            },
        )
        self.assertIn(response.status_code, [200, 302])
        n.refresh_from_db()
        self.assertIsNotNone(n.read_at)
```

- [ ] **Step 2: Ejecutar test — debe fallar**

```bash
make test
```
Esperado: FAIL — la acción `mark_as_read` no existe aún.

- [ ] **Step 3: Actualizar `apps/notifications/admin.py`**

```python
from django.contrib import admin
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin
from unfold.decorators import display, action

from .models import Notification, WebhookEndpoint


@admin.register(Notification)
class NotificationAdmin(ModelAdmin):
    list_display = ("title", "recipient", "channel", "sent_at", "read_at", "created_at")
    list_filter = ("channel", "sent_at", "read_at")
    list_display_links = ("title",)
    search_fields = ("title", "recipient__username", "recipient__email")
    readonly_fields = ("recipient", "title", "body", "channel", "sent_at", "read_at", "payload", "created_at")
    date_hierarchy = "created_at"
    warn_unsaved_change = True
    actions = ["mark_as_read"]

    fieldsets = (
        (_("Mensaje"), {
            "fields": ("recipient", "title", "body", "channel"),
            "classes": ["tab"],
        }),
        (_("Estado"), {
            "fields": ("sent_at", "read_at", "created_at"),
            "classes": ["tab"],
        }),
        (_("Payload"), {
            "fields": ("payload",),
            "classes": ["tab"],
        }),
    )

    @action(description=_("Marcar seleccionadas como leídas"))
    def mark_as_read(self, request, queryset):
        updated = queryset.filter(read_at__isnull=True).update(read_at=timezone.now())
        self.message_user(request, _(f"{updated} notificaciones marcadas como leídas."))

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return obj is None


@admin.register(WebhookEndpoint)
class WebhookEndpointAdmin(ModelAdmin):
    list_display = ("show_url", "user", "show_signed", "show_active")
    list_display_links = ("show_url",)
    list_filter = ("is_active",)
    search_fields = ("url", "user__username")
    compressed_fields = True
    warn_unsaved_change = True
    change_form_after_template = "notifications/webhook_endpoint_guide.html"

    fieldsets = (
        (
            _("Endpoint"),
            {
                "fields": ("user", "url", "is_active"),
                "description": _(
                    "El sistema enviará un HTTP POST a esta URL cada vez que se dispare "
                    "una notificación con <code>channel='webhook'</code> para el usuario seleccionado."
                ),
            },
        ),
        (
            _("Seguridad"),
            {
                "fields": ("secret",),
                "description": _(
                    "Si se configura un secreto, cada POST incluirá el header "
                    "<code>X-Signature: sha256=&lt;hmac&gt;</code> firmado con HMAC-SHA256. "
                    "Ver la guía de integración abajo para verificarlo en tu receptor."
                ),
            },
        ),
    )

    @display(description=_("URL"), ordering="url")
    def show_url(self, obj):
        from urllib.parse import urlparse
        parsed = urlparse(obj.url)
        domain = parsed.netloc or obj.url
        short = domain[:50] + "…" if len(domain) > 50 else domain
        return f'{short}<br><span style="font-size:11px;color:#9ca3af">{obj.url}</span>'

    show_url.allow_tags = True

    @display(
        description=_("Firmado"),
        label={"signed": "success", "unsigned": "warning"},
    )
    def show_signed(self, obj):
        return "signed" if obj.secret else "unsigned"

    @display(
        description=_("Activo"),
        boolean=True,
        ordering="is_active",
    )
    def show_active(self, obj):
        return obj.is_active
```

- [ ] **Step 4: Actualizar `apps/audit/admin.py`**

```python
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin

from .models import AuditLog


@admin.register(AuditLog)
class AuditLogAdmin(ModelAdmin):
    list_display = ("timestamp", "user", "action", "model_name", "object_repr", "ip_address")
    list_display_links = ("timestamp",)
    list_filter = ("action", "model_name", "timestamp")
    search_fields = ("user__username", "object_repr", "model_name", "ip_address")
    date_hierarchy = "timestamp"
    compressed_fields = True
    show_full_result_count = False
    warn_unsaved_change = True
    readonly_fields = (
        "user", "action", "model_name", "object_id", "object_repr",
        "changes", "ip_address", "user_agent", "timestamp",
    )

    fieldsets = (
        (_("Evento"), {
            "fields": ("user", "action", "timestamp", "ip_address", "user_agent"),
            "classes": ["tab"],
        }),
        (_("Objeto"), {
            "fields": ("model_name", "object_id", "object_repr"),
            "classes": ["tab"],
        }),
        (_("Cambios"), {
            "fields": ("changes",),
            "classes": ["tab"],
        }),
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
```

- [ ] **Step 5: Actualizar `apps/core/admin.py`**

```python
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from unfold.admin import ModelAdmin

from .models import User


@admin.register(User)
class UserAdmin(ModelAdmin, BaseUserAdmin):
    list_display = ("username", "email", "role", "is_staff", "is_active", "erp_employee_id")
    list_display_links = ("username",)
    list_filter = ("role", "is_staff", "is_active")
    search_fields = ("username", "email", "erp_employee_id")
    compressed_fields = True
    warn_unsaved_change = True
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Información adicional", {"fields": ("role", "erp_employee_id")}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("Información adicional", {"fields": ("role", "erp_employee_id")}),
    )
```

- [ ] **Step 6: Actualizar `apps/config/admin.py`**

Agregar `warn_unsaved_change = True` y `list_display_links = ("key_display",)` a `SiteConfigAdmin`. El archivo completo queda:

```python
from django.contrib import admin
from django.db.models import Case, IntegerField, Value, When
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin

from .forms import SiteConfigForm
from .models import SiteConfig


_TYPE_COLORS = {
    SiteConfig.ValueType.STR: ("bg-blue-100 text-blue-800", "Texto"),
    SiteConfig.ValueType.INT: ("bg-purple-100 text-purple-800", "Entero"),
    SiteConfig.ValueType.BOOL: ("bg-green-100 text-green-800", "Bool"),
    SiteConfig.ValueType.JSON: ("bg-yellow-100 text-yellow-800", "JSON"),
}


@admin.register(SiteConfig)
class SiteConfigAdmin(ModelAdmin):
    form = SiteConfigForm
    list_display = ("key_display", "value_type_badge", "visibility_badge", "description_short", "value_preview")
    list_display_links = ("key_display",)
    list_filter = ("value_type", "is_public")
    search_fields = ("key", "description")
    ordering = ("key",)
    warn_unsaved_change = True

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        group_cases = [
            When(key__startswith="site_", then=Value(1)),
            When(key__in=["contact_email", "support_email"], then=Value(1)),
            When(key__in=["max_upload_size_mb", "session_timeout_minutes", "items_per_page"], then=Value(2)),
            When(key__startswith="enable_", then=Value(3)),
            When(key__startswith="email_", then=Value(4)),
        ]
        return qs.annotate(
            group_order=Case(*group_cases, default=Value(9), output_field=IntegerField())
        ).order_by("group_order", "key")

    @admin.display(description=_("Clave"))
    def key_display(self, obj):
        return format_html(
            '<code class="font-mono text-sm bg-gray-100 dark:bg-gray-800 px-2 py-0.5 rounded">{}</code>',
            obj.key,
        )

    @admin.display(description=_("Tipo"))
    def value_type_badge(self, obj):
        css, label = _TYPE_COLORS.get(obj.value_type, ("bg-gray-100 text-gray-800", obj.value_type))
        return format_html(
            '<span class="text-xs font-medium px-2 py-0.5 rounded-full {}">{}</span>',
            css,
            label,
        )

    @admin.display(description=_("Visibilidad"), boolean=False)
    def visibility_badge(self, obj):
        if obj.is_public:
            return format_html(
                '<span class="text-xs font-medium px-2 py-0.5 rounded-full bg-emerald-100 text-emerald-800">{}</span>',
                _("Pública"),
            )
        return format_html(
            '<span class="text-xs font-medium px-2 py-0.5 rounded-full bg-gray-100 text-gray-500">{}</span>',
            _("Privada"),
        )

    @admin.display(description=_("Descripción"))
    def description_short(self, obj):
        if not obj.description:
            return "—"
        return obj.description

    @admin.display(description=_("Valor"))
    def value_preview(self, obj):
        text = obj.value or ""
        if len(text) > 60:
            text = text[:60] + "…"
        return text

    @admin.display(description=_("tipo de valor"))
    def value_type_display(self, obj):
        css, label = _TYPE_COLORS.get(obj.value_type, ("bg-gray-100 text-gray-800", obj.value_type))
        return format_html(
            '<span class="text-xs font-medium px-2 py-0.5 rounded-full {}">{}</span>',
            css,
            label,
        )

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ("key", "value_type_display")
        return ()

    def get_fieldsets(self, request, obj=None):
        if obj:
            return (
                (None, {"fields": ("key", "value_type_display", "value")}),
                (_("Metadatos"), {"fields": ("description", "is_public")}),
            )
        return (
            (None, {"fields": ("key", "value_type", "value")}),
            (_("Metadatos"), {"fields": ("description", "is_public")}),
        )

    def has_delete_permission(self, request, obj=None):
        return False
```

- [ ] **Step 7: Actualizar `apps/permissions/admin.py`**

```python
from django.contrib import admin
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin, TabularInline

from .models import ObjectPermission, Role, UserRole

admin.site.unregister(Group)


class UserRoleInline(TabularInline):
    model = UserRole
    extra = 0
    fields = ("role", "assigned_by", "assigned_at")
    readonly_fields = ("assigned_at",)
    verbose_name = _("rol asignado")
    verbose_name_plural = _("roles asignados")


@admin.register(Role)
class RoleAdmin(ModelAdmin):
    list_display = ("name", "description", "user_count")
    list_display_links = ("name",)
    search_fields = ("name", "description")
    filter_horizontal = ("permissions",)
    compressed_fields = True
    warn_unsaved_change = True

    @admin.display(description=_("usuarios"))
    def user_count(self, obj):
        return obj.user_roles.count()


@admin.register(UserRole)
class UserRoleAdmin(ModelAdmin):
    list_display = ("user", "role", "assigned_by", "assigned_at")
    list_display_links = ("user",)
    list_filter = ("role",)
    search_fields = ("user__username", "role__name")
    readonly_fields = ("assigned_at",)
    compressed_fields = True
    warn_unsaved_change = True


@admin.register(ObjectPermission)
class ObjectPermissionAdmin(ModelAdmin):
    list_display = ("user", "content_type", "object_id", "permission")
    list_display_links = ("user",)
    list_filter = ("content_type",)
    search_fields = ("user__username", "object_id")
    warn_unsaved_change = True
```

- [ ] **Step 8: Ejecutar todos los tests**

```bash
make test
```
Esperado: PASS completo — incluyendo el test de bulk action `mark_as_read`.

- [ ] **Step 9: Commit**

```bash
git add apps/core/admin.py apps/audit/admin.py apps/notifications/admin.py apps/config/admin.py apps/permissions/admin.py
git commit -m "feat: Unfold UX improvements across all ModelAdmin (tabs, compressed, warn_unsaved, bulk action)"
```

---

## Task 6: Verificación final e integración

- [ ] **Step 1: Ejecutar la suite completa de tests**

```bash
make test
```
Esperado: todos los tests PASS, sin errores.

- [ ] **Step 2: Verificar el admin completo en el browser**

```bash
make up
```

Checklist manual:
- [ ] `/admin/` muestra el dashboard con stat cards, gráfica y listas
- [ ] El bell icon aparece en el header y muestra badge cuando hay notificaciones no leídas
- [ ] Al hacer click en el bell se abre el dropdown con notificaciones
- [ ] El badge se actualiza a 0 después de abrir el dropdown
- [ ] El polling cada 30s funciona (verificar en Network tab del browser)
- [ ] `/admin/notifications/notification/` muestra tabs en el change form
- [ ] `/admin/audit/auditlog/` muestra tabs en el change form
- [ ] El bulk action "Marcar como leídas" funciona en la lista de notificaciones
- [ ] Dark mode funciona en el dashboard y bell icon

- [ ] **Step 3: Commit final si todo está bien**

```bash
git add .
git commit -m "feat: complete UX/UI admin upgrade — htmx notifications, dashboard, Unfold improvements"
```
