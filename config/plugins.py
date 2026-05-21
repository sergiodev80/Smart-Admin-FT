import importlib


def autoregister_plugins(installed_apps, middleware, settings_module):
    """Read plugin_* attributes from each AppConfig and apply them.

    Imports AppConfig classes directly from each app's apps.py module,
    without going through django.apps registry (which isn't ready at settings load time).
    """
    url_patterns = []

    for app_label in installed_apps:
        config_class = _load_app_config_class(app_label)
        if config_class is None:
            continue

        for url_def in getattr(config_class, "plugin_urls", []):
            url_patterns.append(url_def)

        for mw_def in getattr(config_class, "plugin_middleware", []):
            _insert_middleware(middleware, mw_def)

        for key, value in getattr(config_class, "plugin_settings", {}).items():
            if key not in settings_module:
                settings_module[key] = value

    return url_patterns


def _load_app_config_class(app_label):
    """Import the AppConfig class from app_label.apps without instantiating it."""
    try:
        apps_module = importlib.import_module(f"{app_label}.apps")
    except (ImportError, ModuleNotFoundError):
        return None

    # Find the first AppConfig subclass defined in the module
    from django.apps import AppConfig
    for attr in vars(apps_module).values():
        if (
            isinstance(attr, type)
            and issubclass(attr, AppConfig)
            and attr is not AppConfig
            and getattr(attr, "name", None) == app_label
        ):
            return attr
    return None


def _insert_middleware(middleware, mw_def):
    target = mw_def["middleware"]
    if target in middleware:
        return
    after = mw_def.get("insert_after")
    if after:
        for i, mw in enumerate(middleware):
            if after in mw:
                middleware.insert(i + 1, target)
                return
    middleware.append(target)
