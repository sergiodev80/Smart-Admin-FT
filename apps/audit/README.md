# apps/audit

Full activity log: admin CRUD, login, logout, and optional navigation tracking.

## Activation

1. Uncomment `"apps.audit"` in `LOCAL_APPS` in `config/settings/base.py`
2. Run `make migrate`

## Admin CRUD tracking

Add `AuditMixin` to any `ModelAdmin` to auto-log create/update/delete:

```python
from apps.audit.mixins import AuditMixin
from unfold.admin import ModelAdmin

class MyModelAdmin(AuditMixin, ModelAdmin):
    ...
```

## Navigation tracking (optional)

Add to `MIDDLEWARE` in `config/settings/base.py`:

```python
"apps.audit.middleware.AuditMiddleware",
```

This logs every authenticated GET request as a `view` action.
