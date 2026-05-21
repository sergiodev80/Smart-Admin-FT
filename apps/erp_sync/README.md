# apps/erp_sync — Ejemplo de integración con sistema externo

App de ejemplo que muestra el patrón `*Service` para conectar sistemas externos (ERP, CRM, APIs de terceros, FTP, etc.).

## Cuándo usar este patrón

Cualquier acceso a un sistema fuera de Django (API REST, base de datos externa, servicio SOAP, FTP) debe vivir en una clase `*Service` dentro de su propia app. Nunca conectar sistemas externos directamente desde vistas, admin o señales.

## Activación

1. Añadir `"apps.erp_sync"` en `LOCAL_APPS` en `config/settings/base.py`
2. No requiere migraciones (no define modelos propios)

## Implementación

Reemplazar el stub en `services.py` con la conexión real al sistema externo:

```python
# apps/erp_sync/services.py
import logging
import requests

logger = logging.getLogger(__name__)


class ERPUserService:
    BASE_URL = "https://erp.ejemplo.com/api"

    @staticmethod
    def find_by_email(email: str):
        try:
            response = requests.get(
                f"{ERPUserService.BASE_URL}/users",
                params={"email": email},
                timeout=5,
            )
            response.raise_for_status()
            data = response.json()
            return data if data else None
        except Exception as e:
            logger.error("ERPUserService.find_by_email error: %s", e)
            return None
```

## Patrón de uso desde otras apps

```python
from apps.erp_sync.services import ERPUserService

erp_user = ERPUserService.find_by_email(request.user.email)
if erp_user:
    # usar datos del ERP
    pass
```

## Variables de entorno recomendadas

Añadir al `.env.example` del proyecto:

```bash
ERP_BASE_URL=https://erp.ejemplo.com/api
ERP_API_KEY=
```

Y leerlas en `apps.py` vía `plugin_settings`:

```python
plugin_settings = {
    "ERP_BASE_URL": os.getenv("ERP_BASE_URL", ""),
    "ERP_API_KEY": os.getenv("ERP_API_KEY", ""),
}
```
