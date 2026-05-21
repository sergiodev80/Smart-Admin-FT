from django.contrib.auth import get_user_model
from django.test import TestCase, RequestFactory
from django.utils import timezone

User = get_user_model()


class NotificationViewsTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="viewuser", password="pass", is_staff=True)
        self.client.login(username="viewuser", password="pass")

    def _htmx_get(self, url):
        return self.client.get(url, HTTP_HX_REQUEST="true")

    def _htmx_post(self, url):
        return self.client.post(url, HTTP_HX_REQUEST="true")

    def test_unread_count_requires_login(self):
        self.client.logout()
        response = self.client.get("/admin/notifications/unread-count/", HTTP_HX_REQUEST="true")
        self.assertEqual(response.status_code, 302)

    def test_unread_count_returns_200(self):
        response = self._htmx_get("/admin/notifications/unread-count/")
        self.assertEqual(response.status_code, 200)

    def test_unread_count_shows_zero_when_no_notifications(self):
        response = self._htmx_get("/admin/notifications/unread-count/")
        self.assertContains(response, "0")

    def test_unread_count_shows_correct_number(self):
        from apps.notifications.models import Notification
        Notification.objects.create(
            recipient=self.user,
            title="Test",
            body="Body",
            channel="in_app",
        )
        response = self._htmx_get("/admin/notifications/unread-count/")
        self.assertContains(response, "1")

    def test_unread_list_returns_200(self):
        response = self._htmx_get("/admin/notifications/unread-list/")
        self.assertEqual(response.status_code, 200)

    def test_unread_list_shows_notification_title(self):
        from apps.notifications.models import Notification
        Notification.objects.create(
            recipient=self.user,
            title="Mi notificacion",
            body="Body",
            channel="in_app",
        )
        response = self._htmx_get("/admin/notifications/unread-list/")
        self.assertContains(response, "Mi notificacion")

    def test_mark_read_marks_all_as_read(self):
        from apps.notifications.models import Notification
        Notification.objects.create(
            recipient=self.user, title="A", body="B", channel="in_app"
        )
        self._htmx_post("/admin/notifications/mark-read/")
        self.assertEqual(
            Notification.objects.filter(recipient=self.user, read_at__isnull=True).count(),
            0,
        )

    def test_mark_read_returns_badge_with_zero(self):
        response = self._htmx_post("/admin/notifications/mark-read/")
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "0")
