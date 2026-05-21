import json
import logging

logger = logging.getLogger(__name__)

_cache: dict = {}


class ConfigService:
    @staticmethod
    def get(key: str, default=None):
        if key in _cache:
            return _cache[key]
        try:
            from apps.config.models import SiteConfig
            cfg = SiteConfig.objects.get(key=key)
            value = ConfigService._cast(cfg.value, cfg.value_type)
            _cache[key] = value
            return value
        except Exception:
            return default

    @staticmethod
    def set(key: str, value) -> None:
        from apps.config.models import SiteConfig
        cfg = SiteConfig.objects.get(key=key)
        cfg.value = str(value)
        cfg.save()

    @staticmethod
    def invalidate(key: str) -> None:
        _cache.pop(key, None)

    @staticmethod
    def _cast(value: str, value_type: str):
        try:
            if value_type == "int":
                return int(value)
            if value_type == "bool":
                return value.lower() in ("true", "1", "yes")
            if value_type == "json":
                return json.loads(value)
            return value
        except (ValueError, json.JSONDecodeError) as e:
            logger.error("ConfigService cast error for value %r as %s: %s", value, value_type, e)
            return value
