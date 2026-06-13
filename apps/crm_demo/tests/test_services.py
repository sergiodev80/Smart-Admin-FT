from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.crm_demo.models import Contact, Purchase
from apps.crm_demo.services import ContactService

User = get_user_model()


class ContactServiceTest(TestCase):
    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username="admin_test",
            email="admin@test.com",
            password="testpass123",
        )

    def test_create_contact_sends_in_app_notification(self):
        with patch("apps.crm_demo.services.NotificationService.send") as mock_send:
            contact = ContactService.create(
                {"name": "Ana", "email": "ana@test.com", "status": "lead"},
                created_by=self.admin_user,
            )
        self.assertIsNotNone(contact.pk)
        mock_send.assert_called_once()
        call_kwargs = mock_send.call_args
        channels = call_kwargs.kwargs.get("channels") or call_kwargs.args[3]
        self.assertIn("in_app", channels)

    def test_create_contact_raises_when_max_exceeded(self):
        with patch("apps.crm_demo.services.ConfigService.get", return_value=1):
            Contact.objects.create(name="Existing", email="existing@test.com")
            with self.assertRaises(ValueError) as ctx:
                ContactService.create(
                    {"name": "New", "email": "new@test.com"},
                    created_by=self.admin_user,
                )
        self.assertIn("máximo", str(ctx.exception))

    def test_register_purchase_sends_email_notification(self):
        contact = Contact.objects.create(name="Bob", email="bob@test.com")
        with patch("apps.crm_demo.services.NotificationService.send") as mock_send:
            purchase = ContactService.register_purchase(
                contact,
                {"amount": "99.99", "description": "Producto A", "date": "2026-01-01"},
                created_by=self.admin_user,
            )
        self.assertIsNotNone(purchase.pk)
        mock_send.assert_called_once()
        call_kwargs = mock_send.call_args
        channels = call_kwargs.kwargs.get("channels") or call_kwargs.args[3]
        self.assertIn("email", channels)
