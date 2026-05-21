from django.test import TestCase


class SiteConfigModelTest(TestCase):
    def test_create_str_config(self):
        from apps.config.models import SiteConfig
        cfg = SiteConfig.objects.create(
            key="site_name",
            value="Acme Corp",
            value_type="str",
            description="Nombre del sitio",
        )
        self.assertEqual(str(cfg), "site_name")

    def test_create_int_config(self):
        from apps.config.models import SiteConfig
        cfg = SiteConfig.objects.create(key="max_items", value="50", value_type="int")
        self.assertEqual(str(cfg), "max_items")

    def test_key_is_unique(self):
        from apps.config.models import SiteConfig
        from django.db import IntegrityError
        SiteConfig.objects.create(key="dup_key", value="1", value_type="str")
        with self.assertRaises(IntegrityError):
            SiteConfig.objects.create(key="dup_key", value="2", value_type="str")


class ConfigServiceTest(TestCase):
    def setUp(self):
        from apps.config.models import SiteConfig
        SiteConfig.objects.create(key="greeting", value="Hello", value_type="str")
        SiteConfig.objects.create(key="max_size", value="100", value_type="int")
        SiteConfig.objects.create(key="feature_on", value="true", value_type="bool")
        SiteConfig.objects.create(key="meta", value='{"a": 1}', value_type="json")

    def test_get_str(self):
        from apps.config.services import ConfigService
        self.assertEqual(ConfigService.get("greeting"), "Hello")

    def test_get_int(self):
        from apps.config.services import ConfigService
        self.assertEqual(ConfigService.get("max_size"), 100)

    def test_get_bool_true(self):
        from apps.config.services import ConfigService
        self.assertTrue(ConfigService.get("feature_on"))

    def test_get_json(self):
        from apps.config.services import ConfigService
        self.assertEqual(ConfigService.get("meta"), {"a": 1})

    def test_get_missing_returns_default(self):
        from apps.config.services import ConfigService
        self.assertIsNone(ConfigService.get("nonexistent"))
        self.assertEqual(ConfigService.get("nonexistent", default="fallback"), "fallback")

    def test_set_updates_value(self):
        from apps.config.services import ConfigService
        ConfigService.set("greeting", "Hola")
        self.assertEqual(ConfigService.get("greeting"), "Hola")

    def test_cache_is_invalidated_on_save(self):
        from apps.config.services import ConfigService
        from apps.config.models import SiteConfig
        ConfigService.get("greeting")  # populate cache
        cfg = SiteConfig.objects.get(key="greeting")
        cfg.value = "Hi"
        cfg.save()
        self.assertEqual(ConfigService.get("greeting"), "Hi")


class ConfigAdminRegisteredTest(TestCase):
    def test_siteconfig_registered(self):
        from django.contrib import admin
        from apps.config.models import SiteConfig
        self.assertIn(SiteConfig, admin.site._registry)
