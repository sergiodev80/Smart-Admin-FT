# apps/config

Dynamic site settings stored in the database. Edit values from the admin without touching code.

## Activation

1. Uncomment `"apps.config"` in `LOCAL_APPS` in `config/settings/base.py`
2. Run `make migrate`

## Usage

```python
from apps.config.services import ConfigService

value = ConfigService.get("my_key", default="fallback")
ConfigService.set("my_key", "new_value")
```

## Value types

| Type | Example value | Returns |
|------|--------------|---------|
| `str` | `"Hello"` | `"Hello"` |
| `int` | `"42"` | `42` |
| `bool` | `"true"` | `True` |
| `json` | `'{"a": 1}'` | `{"a": 1}` |

## Template context

Configs with `is_public=True` are available as `public_configs` in templates
once you add `apps.config.context_processors.public_configs` to `TEMPLATES[0]["OPTIONS"]["context_processors"]`.
