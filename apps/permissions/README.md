# apps/permissions

Granular role and per-object permission management.

## Activation

1. Uncomment `"apps.permissions"` in `LOCAL_APPS` in `config/settings/base.py`
2. Run `make migrate`
3. Load default roles:
   ```bash
   docker compose -f docker-compose.dev.yml exec web_dev python manage.py loaddata apps/permissions/fixtures/default_roles.json
   ```

## Roles

Roles group Django permissions and are assigned to users via `UserRole`.
The default roles (`admin`, `pm`, `translator`, `reviewer`) match the string roles in `core.User`.

## Per-object permissions

`ObjectPermission` grants a specific user permission on a specific model instance:

```python
from apps.permissions.models import ObjectPermission
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import Permission

ObjectPermission.objects.create(
    user=user,
    content_type=ContentType.objects.get_for_model(MyModel),
    object_id=str(instance.pk),
    permission=Permission.objects.get(codename="change_mymodel"),
)
```
