from unittest.mock import MagicMock, patch

from django.contrib.auth import get_user_model
from django.test import TestCase

User = get_user_model()


class NotificationModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="recipient", password="pass")

    def test_create_in_app_notification(self):
        from apps.notifications.models import Notification
        n = Notification.objects.create(
            recipient=self.user,
            title="Test",
            body="Body",
            channel=Notification.Channel.IN_APP,
        )
        self.assertIsNone(n.read_at)
        self.assertIsNone(n.sent_at)

    def test_str_includes_title(self):
        from apps.notifications.models import Notification
        n = Notification.objects.create(
            recipient=self.user,
            title="Hello",
            body="World",
            channel=Notification.Channel.IN_APP,
        )
        self.assertIn("Hello", str(n))

    def test_webhook_endpoint_str(self):
        from apps.notifications.models import WebhookEndpoint
        ep = WebhookEndpoint.objects.create(
            user=self.user,
            url="https://example.com/hook",
            secret="mysecret",
        )
        self.assertIn("example.com", str(ep))


class NotificationServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username="notif_user",
            email="notif@example.com",
            password="pass",
        )

    def test_send_in_app_creates_record(self):
        from apps.notifications.models import Notification
        from apps.notifications.services import NotificationService
        NotificationService.send(
            user=self.user,
            title="Welcome",
            body="Hello!",
            channels=["in_app"],
        )
        self.assertTrue(
            Notification.objects.filter(recipient=self.user, title="Welcome").exists()
        )

    @patch("apps.notifications.services.send_mail")
    def test_send_email_calls_send_mail(self, mock_send):
        from apps.notifications.services import NotificationService
        NotificationService.send(
            user=self.user,
            title="Email Alert",
            body="Check this out",
            channels=["email"],
        )
        mock_send.assert_called_once()
        args, kwargs = mock_send.call_args
        recipient_list = kwargs.get("recipient_list") or args[3]
        self.assertIn("notif@example.com", recipient_list)

    @patch("apps.notifications.services.requests.post")
    def test_send_webhook_posts_to_endpoint(self, mock_post):
        from apps.notifications.models import WebhookEndpoint
        from apps.notifications.services import NotificationService
        mock_post.return_value = MagicMock(status_code=200)
        WebhookEndpoint.objects.create(
            user=self.user,
            url="https://example.com/hook",
            secret="secret123",
            is_active=True,
        )
        NotificationService.send(
            user=self.user,
            title="Hook",
            body="Fired",
            channels=["webhook"],
            payload={"event": "test"},
        )
        mock_post.assert_called_once()

    @patch("apps.notifications.services.requests.post")
    def test_webhook_signature_header_present(self, mock_post):
        from apps.notifications.models import WebhookEndpoint
        from apps.notifications.services import NotificationService
        mock_post.return_value = MagicMock(status_code=200)
        WebhookEndpoint.objects.create(
            user=self.user,
            url="https://hook.example.com/",
            secret="topsecret",
            is_active=True,
        )
        NotificationService.send(
            user=self.user,
            title="Signed",
            body="Payload",
            channels=["webhook"],
            payload={"x": 1},
        )
        headers = mock_post.call_args[1].get("headers", {})
        self.assertIn("X-Signature", headers)


class NotificationAdminBulkActionTest(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            username="admin_bulk", password="pass", email="admin_bulk@example.com"
        )
        self.user = User.objects.create_user(username="target_bulk", password="pass")
        self.client.login(username="admin_bulk", password="pass")

    def test_mark_as_read_action(self):
        from apps.notifications.models import Notification
        n = Notification.objects.create(
            recipient=self.user,
            title="Bulk test",
            body="Body",
            channel="in_app",
        )
        response = self.client.post(
            "/admin/notifications/notification/",
            {
                "action": "mark_as_read",
                "_selected_action": [n.pk],
            },
        )
        self.assertIn(response.status_code, [200, 302])
        n.refresh_from_db()
        self.assertIsNotNone(n.read_at)


class NotificationAdminRegisteredTest(TestCase):
    def test_notification_registered(self):
        from django.contrib import admin
        from apps.notifications.models import Notification
        self.assertIn(Notification, admin.site._registry)

    def test_webhook_endpoint_registered(self):
        from django.contrib import admin
        from apps.notifications.models import WebhookEndpoint
        self.assertIn(WebhookEndpoint, admin.site._registry)
