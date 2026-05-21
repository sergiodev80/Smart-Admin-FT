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

    def test_dashboard_callback_returns_context_with_recent_users(self):
        from apps.core.dashboard import dashboard_callback
        request = self.factory.get("/admin/")
        request.user = self.user
        context = {}
        result = dashboard_callback(request, context)
        self.assertIn("recent_users", result)

    def test_dashboard_callback_returns_context_with_recent_audit(self):
        from apps.core.dashboard import dashboard_callback
        request = self.factory.get("/admin/")
        request.user = self.user
        context = {}
        result = dashboard_callback(request, context)
        self.assertIn("recent_audit", result)
