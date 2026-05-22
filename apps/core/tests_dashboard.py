from django.contrib.auth import get_user_model
from django.test import TestCase, RequestFactory

User = get_user_model()


class DashboardCallbackTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="dashuser", password="pass")
        self.factory = RequestFactory()

    def test_dashboard_callback_returns_context_with_stat_cards(self):
        from apps.core.dashboard import dashboard_callback
        request = self.factory.get("/admin/")
        request.user = self.user
        context = {}
        result = dashboard_callback(request, context)
        self.assertIn("stat_cards", result)
        self.assertIsInstance(result["stat_cards"], list)
        self.assertGreater(len(result["stat_cards"]), 0)

    def test_dashboard_callback_stat_cards_have_required_keys(self):
        from apps.core.dashboard import dashboard_callback
        request = self.factory.get("/admin/")
        request.user = self.user
        context = {}
        result = dashboard_callback(request, context)
        for card in result["stat_cards"]:
            self.assertIn("title", card)
            self.assertIn("value", card)
            self.assertIn("icon", card)

    def test_dashboard_callback_returns_context_with_users_table(self):
        from apps.core.dashboard import dashboard_callback
        request = self.factory.get("/admin/")
        request.user = self.user
        context = {}
        result = dashboard_callback(request, context)
        self.assertIn("users_table", result)
        self.assertTrue(hasattr(result["users_table"], "headers"))
        self.assertTrue(hasattr(result["users_table"], "rows"))

    def test_dashboard_callback_returns_context_with_audit_table(self):
        from apps.core.dashboard import dashboard_callback
        request = self.factory.get("/admin/")
        request.user = self.user
        context = {}
        result = dashboard_callback(request, context)
        self.assertIn("audit_table", result)
        self.assertTrue(hasattr(result["audit_table"], "headers"))
        self.assertTrue(hasattr(result["audit_table"], "rows"))

    def test_chart_data_has_7_days(self):
        from apps.core.dashboard import dashboard_callback
        import json
        request = self.factory.get("/admin/")
        request.user = self.user
        result = dashboard_callback(request, {})
        chart = json.loads(result["chart_data"])
        self.assertEqual(len(chart["labels"]), 7)
        self.assertEqual(len(chart["datasets"][0]["data"]), 7)

    def test_chart_data_reflects_audit_logs(self):
        from apps.audit.models import AuditLog
        from apps.core.dashboard import dashboard_callback
        import json
        AuditLog.objects.create(
            user=self.user, action="create", model_name="Test", object_repr="obj"
        )
        request = self.factory.get("/admin/")
        request.user = self.user
        result = dashboard_callback(request, {})
        chart = json.loads(result["chart_data"])
        self.assertGreater(sum(chart["datasets"][0]["data"]), 0)
