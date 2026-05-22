# CRM Demo — Spec de diseño

**Fecha:** 2026-05-22
**App:** `apps/crm_demo`
**Propósito:** App demo para staff interno que exhibe los 12 componentes UI del proyecto en un flujo CRM real (contactos, historial de compras, emails y llamadas). Sirve como guía de referencia para la IA al construir otros módulos.

---

## Enfoque elegido

**Opción A — Una sola vista split panel.** La página `/admin/crm-demo/contacts/` es el hub central con todos los componentes integrados en un flujo cohesivo.

---

## Modelos

```python
class Contact(models.Model):
    STATUS_CHOICES = [
        ("lead", "Lead"),
        ("prospect", "Prospecto"),
        ("client", "Cliente"),
        ("inactive", "Inactivo"),
    ]
    name       = CharField(max_length=200)
    email      = EmailField(unique=True)
    phone      = CharField(max_length=50, blank=True)
    company    = CharField(max_length=200, blank=True)
    status     = CharField(max_length=20, choices=STATUS_CHOICES, default="lead")
    created_at = DateTimeField(auto_now_add=True)

class Purchase(models.Model):
    contact     = FK(Contact, related_name="purchases", on_delete=CASCADE)
    amount      = DecimalField(max_digits=10, decimal_places=2)
    description = CharField(max_length=300)
    date        = DateField()

class EmailLog(models.Model):
    DIRECTION = [("in", "Entrante"), ("out", "Saliente")]
    contact   = FK(Contact, related_name="email_logs", on_delete=CASCADE)
    subject   = CharField(max_length=200)
    body      = TextField(blank=True)
    date      = DateTimeField()
    direction = CharField(max_length=3, choices=DIRECTION)

class CallLog(models.Model):
    DIRECTION = [("in", "Entrante"), ("out", "Saliente")]
    contact          = FK(Contact, related_name="call_logs", on_delete=CASCADE)
    duration_minutes = PositiveIntegerField()
    notes            = TextField(blank=True)
    date             = DateTimeField()
    direction        = CharField(max_length=3, choices=DIRECTION)

class SocialProfile(models.Model):
    NETWORK_CHOICES = [
        ("linkedin", "LinkedIn"),
        ("twitter", "Twitter"),
        ("instagram", "Instagram"),
        ("facebook", "Facebook"),
    ]
    contact = FK(Contact, related_name="social_profiles", on_delete=CASCADE)
    network = CharField(max_length=20, choices=NETWORK_CHOICES)
    url     = URLField()

    class Meta:
        unique_together = [("contact", "network")]
```

---

## Services

```python
class ContactService:
    @staticmethod
    def create(data: dict, created_by) -> Contact:
        # 1. Verifica crm_demo_contact_max via ConfigService — lanza ValueError si se supera
        # 2. Crea Contact
        # 3. NotificationService.send(user=admin, title=..., channels=["in_app"])

    @staticmethod
    def register_purchase(contact: Contact, data: dict, created_by) -> Purchase:
        # 1. Crea Purchase
        # 2. NotificationService.send(user=admin, title=..., channels=["email"])
```

No se usan señales — toda la lógica de negocio pasa por `ContactService`.

---

## Estructura de archivos

```
apps/crm_demo/
  __init__.py
  apps.py
  models.py
  services.py
  admin.py
  urls.py
  views.py
  templates/
    crm_demo/
      contact_list.html           — página principal (split panel hub)
      contact_list_items.html     — partial izquierdo (lista + filter_tabs)
      contact_detail.html         — partial derecho (data_list + historiales)
      contact_create_modal.html   — partial modal (modal_content)
  migrations/
    0001_initial.py
    0002_default_config.py        — inserta crm_demo_contact_max = 500
  tests/
    test_models.py
    test_services.py
    test_views.py
```

---

## URLs

Registradas en `AppConfig.plugin_urls` con prefix `admin/crm-demo/`. Todas protegidas con `@staff_member_required`.

```python
urlpatterns = [
    path("contacts/",                   ContactListView,         name="crm_contact_list"),
    path("contacts/items/",             ContactListItemsPartial, name="crm_contact_items"),
    path("contacts/create/",            CreateContactView,       name="crm_contact_create"),
    path("contacts/counts/",            FilterCountsView,        name="crm_contact_counts"),
    path("contacts/<int:pk>/detail/",   ContactDetailPartial,    name="crm_contact_detail"),
    path("contacts/<int:pk>/inline-edit/", InlineEditView,       name="crm_contact_inline_edit"),
    path("contacts/<int:pk>/delete/",   DeleteContactView,       name="crm_contact_delete"),
]
```

---

## Flujo HTMX

```
ContactListView (GET /admin/crm-demo/contacts/)
  └── contact_list.html
        ├── page_header       — título "Gestión de Contactos" + botón "Nuevo contacto"
        │                       hx-get=create/ hx-target=#modal-container
        ├── 4× stat_card      — KPIs calculados en la vista (sin HTMX async)
        ├── filter_tabs       — hx-get=items/?status=X hx-target=#contact-items
        └── split_panel
              ├── panel izq #contact-items  → contact_list_items.html
              │     ├── lista de contactos con inline_edit (phone, company)
              │     └── empty_state si no hay resultados
              └── panel der #contact-detail → vacío inicial con empty_state
                    └── click en contacto → hx-get=<pk>/detail/ hx-target=#contact-detail

ContactDetailPartial (GET /admin/crm-demo/contacts/<pk>/detail/)
  └── contact_detail.html
        ├── skeleton (hx-trigger="load" mientras carga)
        ├── data_list         — campos del contacto (nombre, email, empresa, estado)
        ├── copy_to_clipboard — ID y email
        └── secciones de historial (Purchases / EmailLogs / CallLogs / SocialProfiles)
              └── empty_state si no hay registros en cada sección

InlineEditView
  GET  → retorna inline_edit.html con el form del campo
  PATCH → guarda, retorna inline_edit.html actualizado
           + HX-Trigger: {"showToast": {"message": "...", "level": "success"}}

CreateContactView
  GET  → retorna contact_create_modal.html (modal_content, size="md")
  POST → exitoso: HX-Trigger showToast + HX-Refresh
         error:   retorna modal con errores de validación

DeleteContactView (POST)
  — precedido por confirm_dialog en el template (modo estricto: escribir email)
  → elimina → HX-Trigger showToast + HX-Redirect a lista
```

---

## Los 12 componentes y dónde aparecen

| Componente | Ubicación en la demo |
|---|---|
| `page_header` | Cabecera de `contact_list.html` |
| `stat_card` | 4 KPIs en `contact_list.html` |
| `filter_tabs` | Tabs de estado con contadores en `contact_list.html` |
| `split_panel` | Layout principal de `contact_list.html` |
| `inline_edit` | Editar phone/company desde `contact_list_items.html` |
| `empty_state` | Panel derecho vacío inicial + sin historial en `contact_detail.html` |
| `skeleton` | Carga del detalle en `contact_detail.html` |
| `data_list` | Campos del contacto en `contact_detail.html` |
| `copy_to_clipboard` | ID y email en `contact_detail.html` |
| `modal_content` | Crear contacto desde `contact_create_modal.html` |
| `toast` | Feedback HTMX en guardar, crear, eliminar |
| `confirm_dialog` | Antes de eliminar un contacto (modo estricto) |

---

## Admin (`ContactAdmin`)

```python
class ContactAdmin(AuditMixin, ModelAdmin):
    list_display   = ["name", "email", "company", "status_badge", "created_at"]
    list_filter    = ["status", "created_at"]
    date_hierarchy = "created_at"
    warn_unsaved_changes = True
    fieldsets = [
        (_("Información general"), {"fields": ["name","email","phone","company","status"], "classes": ["tab"]}),
        (_("Historial"),           {"classes": ["tab"]}),  # inlines, no fields directos
    ]
    inlines = [PurchaseInline, EmailLogInline, CallLogInline, SocialProfileInline]
    actions = ["mark_inactive"]
```

`status_badge` retorna HTML con color por estado:
- `lead` → azul, `prospect` → amarillo, `client` → verde, `inactive` → gris

---

## Dashboard widget

`apps/crm_demo/dashboard.py` expone dos funciones:

- `get_crm_cards(request)` → lista de 4 dicts para `stat_card` (total contactos, compras del mes, llamadas hoy, emails enviados hoy)
- `get_recent_contacts_table(request)` → `_Table` con los últimos 5 contactos

Se inyectan en `dashboard_callback` de `config/settings/base.py` con imports dentro de la función (patrón del proyecto para evitar circular imports).

---

## Sidebar

```python
{
    "title": _("CRM Demo"),
    "icon": "contacts",
    "items": [
        {"title": _("Gestión de contactos"), "link": reverse_lazy("crm_contact_list")},
        {"title": _("Contactos (admin)"),    "link": reverse_lazy("admin:crm_demo_contact_changelist")},
    ],
}
```

---

## Integraciones del template

- **`notifications`**: crear Contact → `in_app` al admin; crear Purchase → `email` al admin
- **`audit`**: `AuditMixin` en `ContactAdmin` y `PurchaseInline`
- **`config`**: clave `crm_demo_contact_max` (int, default 500) — insertada en `0002_default_config.py`
- **`permissions`**: roles `crm_viewer` (solo lectura) y `crm_editor` (CRUD completo)

---

## AppConfig

```python
class CrmDemoConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.crm_demo"
    verbose_name = _("CRM Demo")

    plugin_urls = [
        {"prefix": "admin/crm-demo/", "urlconf": "apps.crm_demo.urls"},
    ]
    plugin_middleware = []
    plugin_settings = {}
```

Activar añadiendo `"apps.crm_demo"` a `LOCAL_APPS` en `config/settings/base.py`.

---

## Known Pitfalls aplicables

- **Sin Tailwind utilities** — usar `style=""` inline o variables CSS de Unfold (`bg-base-900`)
- **URLs en `AppConfig`**, nunca en `config/urls.py`
- **`@staff_member_required`** en todas las vistas, no `@login_required`
- **Toast vs Django messages**: acciones HTMX sin redirect → `HX-Trigger showToast`; formularios con redirect → `messages.html`
- **Imports en `dashboard_callback`** dentro del body de la función, no en el top del archivo
- **Inline Edit** debe retornar el componente completo (outerHTML swap para reinicializar Alpine)

---

## Tests críticos

### `test_models.py`
- `Contact.status` rechaza valores fuera de `STATUS_CHOICES`
- `SocialProfile` unique_together `(contact, network)` lanza `IntegrityError`

### `test_services.py`
- `ContactService.create` dispara notificación in-app al admin
- `ContactService.create` lanza `ValueError` si se supera `crm_demo_contact_max`
- `ContactService.register_purchase` dispara notificación email al admin

### `test_views.py`
- `GET /admin/crm-demo/contacts/` → 200 con `is_staff=True`
- `GET /admin/crm-demo/contacts/` → 302 sin autenticación
- `POST /admin/crm-demo/contacts/create/` → crea contacto, retorna `HX-Trigger`
- `PATCH /admin/crm-demo/contacts/<pk>/inline-edit/` → actualiza campo, retorna `HX-Trigger`
- `POST /admin/crm-demo/contacts/<pk>/delete/` → elimina contacto, retorna `HX-Redirect`
