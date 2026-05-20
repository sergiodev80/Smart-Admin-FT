# Smart Admin FT — v2 Design Spec

**Date:** 2026-05-20  
**Status:** Approved  

---

## Overview

Upgrade the Smart Admin FT template from v1 (core only) to v2 by adding four independent, plug-and-play Django apps. Each app can be activated or ignored per project by toggling `LOCAL_APPS` and running migrations.

---

## Transversal Constraints

### UI Design
- All `ModelAdmin` classes inherit from `unfold.admin.ModelAdmin` — no exceptions.
- No custom CSS, no template overrides unless strictly necessary.
- If a needed component is not available natively in Unfold (e.g., notification preview, unread badge counter), pause and consult before implementing. Always choose a pre-built, proven solution.

### i18n
- Every UI string wrapped in `_()` (Python) or `{% trans %}` (templates) from the first commit.
- Covers: `verbose_name`, `verbose_name_plural`, field labels, help texts, error messages, admin action names, column headers.
- Translation files centralized in `locale/es/LC_MESSAGES/django.po` and `locale/en/LC_MESSAGES/django.po` at project root (already in `LOCALE_PATHS`).
- Database content (notification body, config values) is NOT translated — single language in DB.

### Documentation
- Each new app includes a `README.md` with activation instructions.
- `CLAUDE.md` updated with new apps, patterns, and any new `make` commands.

### Testing
- Every new app includes tests in `tests.py` before being considered complete.
- Tests cover: model creation, service methods, admin registration, and signal handling.

---

## Architecture

```
apps/
  core/           — unchanged (User model, access request flow)
  notifications/  — in-app + email + webhook notifications
  audit/          — full activity log (admin CRUD + login/logout + navigation)
  config/         — dynamic site settings (key-value store)
  permissions/    — granular roles and per-object permissions
```

No hard dependencies between the four new apps. Each app communicates via Django signals. `audit` listens to any model via signals. `notifications` can receive triggers from any app.

Each app follows this internal convention:

```
apps/<app>/
  __init__.py
  apps.py
  models.py
  admin.py
  services.py     — business logic only, never in views/admin
  signals.py      — cross-app reactive integrations
  tests.py
  migrations/
  README.md
  locale/         — NOT used; translations go to root locale/
```

---

## App: `apps/notifications`

### Models

**`Notification`**
| Field | Type | Notes |
|-------|------|-------|
| `recipient` | FK `core.User` | Required |
| `title` | CharField(200) | |
| `body` | TextField | |
| `channel` | CharField choices | `in_app`, `email`, `webhook` |
| `read_at` | DateTimeField nullable | null = unread |
| `sent_at` | DateTimeField nullable | null = not yet sent |
| `payload` | JSONField | used for webhook POST body |
| `created_at` | DateTimeField auto | |

**`WebhookEndpoint`**
| Field | Type | Notes |
|-------|------|-------|
| `user` | FK `core.User` | Owner |
| `url` | URLField | Destination |
| `is_active` | BooleanField | |
| `secret` | CharField | For HMAC signing |

### Service: `NotificationService`

```python
NotificationService.send(user, title, body, channels: list, payload=None)
```

- `in_app`: creates `Notification` record
- `email`: sends via Django email using `DEFAULT_FROM_EMAIL`
- `webhook`: HTTP POST to user's active `WebhookEndpoint` with HMAC signature header

### Admin
- `NotificationAdmin`: list view with filters by channel, user, read/unread. Read-only for sent notifications.
- `WebhookEndpointAdmin`: manage endpoints per user.

---

## App: `apps/audit`

### Models

**`AuditLog`**
| Field | Type | Notes |
|-------|------|-------|
| `user` | FK `core.User` nullable | null for system actions |
| `action` | CharField choices | `create`, `update`, `delete`, `login`, `logout`, `view` |
| `model_name` | CharField | e.g. `"core.User"` |
| `object_id` | CharField nullable | PK of affected object |
| `object_repr` | CharField | String representation at time of action |
| `changes` | JSONField nullable | Before/after diff for updates |
| `ip_address` | GenericIPAddressField nullable | |
| `user_agent` | CharField nullable | |
| `timestamp` | DateTimeField auto | |

### Capture mechanisms
- **Admin CRUD**: `AuditMixin` for `ModelAdmin` — overrides `save_model` and `delete_model`
- **Login/Logout**: signals `user_logged_in`, `user_logged_out` from `django.contrib.auth`
- **Navigation**: optional `AuditMiddleware` — logs `view` actions, disabled by default

### Admin
- `AuditLogAdmin`: fully read-only. Filters by user, action, model, date range. No add/edit/delete permissions.

---

## App: `apps/config`

### Models

**`SiteConfig`**
| Field | Type | Notes |
|-------|------|-------|
| `key` | SlugField unique | e.g. `"max_upload_size"` |
| `value` | TextField | Stored as string always |
| `value_type` | CharField choices | `str`, `int`, `bool`, `json` |
| `description` | TextField blank | Human-readable purpose |
| `is_public` | BooleanField default False | Expose to templates via context processor |

### Service: `ConfigService`

```python
ConfigService.get(key, default=None)  # returns cast value
ConfigService.set(key, value)          # updates and invalidates cache
```

- In-memory cache per process, invalidated on `post_save` signal of `SiteConfig`.
- Public configs available in templates via context processor if `is_public=True`.

### Admin
- `SiteConfigAdmin`: inline validation per `value_type`. Displays cast preview.

---

## App: `apps/permissions`

### Models

**`Role`**
| Field | Type | Notes |
|-------|------|-------|
| `name` | CharField unique | |
| `description` | TextField blank | |
| `permissions` | M2M `auth.Permission` | Django native permissions |

**`UserRole`** (through model)
| Field | Type | Notes |
|-------|------|-------|
| `user` | FK `core.User` | |
| `role` | FK `Role` | |
| `assigned_at` | DateTimeField auto | |
| `assigned_by` | FK `core.User` nullable | Auditable |

**`ObjectPermission`**
| Field | Type | Notes |
|-------|------|-------|
| `user` | FK `core.User` | |
| `content_type` | FK `ContentType` | |
| `object_id` | CharField | |
| `permission` | FK `auth.Permission` | |

### Migration from v1 roles
The existing string-based role field on `core.User` (`admin`, `pm`, `translator`, `reviewer`) is preserved. A data migration creates corresponding `Role` objects and assigns them via `UserRole`. No breaking change to existing projects.

### Fixtures
Default roles provided as fixture: `apps/permissions/fixtures/default_roles.json` — creates `admin`, `pm`, `translator`, `reviewer` roles matching v1 string roles.

### Admin
- `RoleAdmin`: manage roles and their Django permissions.
- `UserRoleAdmin` (inline on User): assign roles to users.
- `ObjectPermissionAdmin`: per-object permission management.

---

## settings.py changes

```python
LOCAL_APPS = [
    "apps.core",
    # v2 optional apps — uncomment to activate:
    # "apps.notifications",
    # "apps.audit",
    # "apps.config",
    # "apps.permissions",
]
```

Each app's `AppConfig.ready()` connects its signals.

---

## CLAUDE.md updates

- Add section "Apps v2" describing each app, activation steps, and Service patterns.
- Add `make messages` reminder for new translation strings.
- Document `AuditMixin` usage for new project ModelAdmins.
- Document `ConfigService.get()` usage pattern.

---

## Out of scope

- Real-time notifications (WebSocket / SSE) — not needed for a template base.
- Notification preferences UI for end users — can be added per project.
- Multi-language DB content — UI only.
- Per-app `locale/` directories — all translations go to root `locale/`.
