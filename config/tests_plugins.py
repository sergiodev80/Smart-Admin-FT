from unittest import TestCase
from unittest.mock import patch

from config.plugins import autoregister_plugins, _insert_middleware


class TestInsertMiddleware(TestCase):
    def test_insert_after_known_middleware(self):
        middleware = [
            "django.contrib.sessions.middleware.SessionMiddleware",
            "django.contrib.auth.middleware.AuthenticationMiddleware",
            "django.contrib.messages.middleware.MessageMiddleware",
        ]
        _insert_middleware(middleware, {
            "middleware": "apps.audit.middleware.AuditMiddleware",
            "insert_after": "AuthenticationMiddleware",
        })
        auth_idx = middleware.index("django.contrib.auth.middleware.AuthenticationMiddleware")
        audit_idx = middleware.index("apps.audit.middleware.AuditMiddleware")
        self.assertEqual(audit_idx, auth_idx + 1)

    def test_no_duplicate(self):
        middleware = ["apps.audit.middleware.AuditMiddleware"]
        _insert_middleware(middleware, {
            "middleware": "apps.audit.middleware.AuditMiddleware",
            "insert_after": "AuthenticationMiddleware",
        })
        self.assertEqual(middleware.count("apps.audit.middleware.AuditMiddleware"), 1)

    def test_append_when_insert_after_not_found(self):
        middleware = ["django.middleware.common.CommonMiddleware"]
        _insert_middleware(middleware, {
            "middleware": "apps.audit.middleware.AuditMiddleware",
            "insert_after": "NonExistentMiddleware",
        })
        self.assertEqual(middleware[-1], "apps.audit.middleware.AuditMiddleware")

    def test_append_when_no_insert_after(self):
        middleware = ["django.middleware.common.CommonMiddleware"]
        _insert_middleware(middleware, {
            "middleware": "apps.audit.middleware.AuditMiddleware",
        })
        self.assertEqual(middleware[-1], "apps.audit.middleware.AuditMiddleware")


class FakeConfigWithUrls:
    name = "apps.notifications"
    plugin_urls = [{"prefix": "admin/notifications/", "urlconf": "apps.notifications.urls"}]


class FakeConfigWithMiddleware:
    name = "apps.audit"
    plugin_middleware = [{
        "middleware": "apps.audit.middleware.AuditMiddleware",
        "insert_after": "AuthenticationMiddleware",
    }]


class FakeConfigWithSettings:
    name = "apps.notifications"
    plugin_settings = {"WEBHOOK_SECRET": "from-plugin"}


class FakeConfigEmpty:
    name = "apps.core"


class TestAutoregisterPlugins(TestCase):
    def test_urls_registered(self):
        middleware = []
        settings_module = {}

        with patch("config.plugins._load_app_config_class", return_value=FakeConfigWithUrls):
            urls = autoregister_plugins(["apps.notifications"], middleware, settings_module)

        self.assertEqual(len(urls), 1)
        self.assertEqual(urls[0]["prefix"], "admin/notifications/")

    def test_middleware_inserted(self):
        middleware = ["django.contrib.auth.middleware.AuthenticationMiddleware"]
        settings_module = {}

        with patch("config.plugins._load_app_config_class", return_value=FakeConfigWithMiddleware):
            autoregister_plugins(["apps.audit"], middleware, settings_module)

        self.assertIn("apps.audit.middleware.AuditMiddleware", middleware)

    def test_settings_not_overwrite(self):
        middleware = []
        settings_module = {"WEBHOOK_SECRET": "already-set"}

        with patch("config.plugins._load_app_config_class", return_value=FakeConfigWithSettings):
            autoregister_plugins(["apps.notifications"], middleware, settings_module)

        self.assertEqual(settings_module["WEBHOOK_SECRET"], "already-set")

    def test_settings_injected_when_missing(self):
        middleware = []
        settings_module = {}

        with patch("config.plugins._load_app_config_class", return_value=FakeConfigWithSettings):
            autoregister_plugins(["apps.notifications"], middleware, settings_module)

        self.assertEqual(settings_module["WEBHOOK_SECRET"], "from-plugin")

    def test_app_without_attributes_no_error(self):
        middleware = []
        settings_module = {}

        with patch("config.plugins._load_app_config_class", return_value=FakeConfigEmpty):
            urls = autoregister_plugins(["apps.core"], middleware, settings_module)

        self.assertEqual(urls, [])
        self.assertEqual(middleware, [])
        self.assertEqual(settings_module, {})

    def test_unknown_app_skipped(self):
        with patch("config.plugins._load_app_config_class", return_value=None):
            urls = autoregister_plugins(["apps.nonexistent"], [], {})
        self.assertEqual(urls, [])
