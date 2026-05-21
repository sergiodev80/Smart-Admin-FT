from django.apps import apps as django_apps


def autoregister_plugins(installed_apps, middleware, settings_module):
    """Read plugin_* attributes from each AppConfig and apply them."""
    url_patterns = []

    for app_label in installed_apps:
        try:
            config = django_apps.get_app_config(_app_name(app_label))
        except LookupError:
            continue

        for url_def in getattr(config, "plugin_urls", []):
            url_patterns.append(url_def)

        for mw_def in getattr(config, "plugin_middleware", []):
            _insert_middleware(middleware, mw_def)

        for key, value in getattr(config, "plugin_settings", {}).items():
            if key not in settings_module:
                settings_module[key] = value

    return url_patterns


def _app_name(app_label):
    return app_label.split(".")[-1] if "." in app_label else app_label


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
