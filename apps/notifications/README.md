# apps/notifications

Send notifications via in-app, email, and webhook channels.

## Activation

1. Uncomment `"apps.notifications"` in `LOCAL_APPS` in `config/settings/base.py`
2. Run `make migrate`

## Usage

```python
from apps.notifications.services import NotificationService

NotificationService.send(
    user=request.user,
    title="Nueva tarea asignada",
    body="Tienes una nueva tarea pendiente.",
    channels=["in_app", "email"],
)

# With webhook payload:
NotificationService.send(
    user=user,
    title="Evento",
    body="Descripción",
    channels=["webhook"],
    payload={"event_type": "task.assigned", "task_id": 42},
)
```

## Webhook signing

Webhooks are signed with HMAC-SHA256. The signature is sent in the `X-Signature` header as `sha256=<hex>`.
Configure each user's endpoint secret in `WebhookEndpoint.secret`.
