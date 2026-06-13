import json
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.http import HttpResponse
from django.test import Client, TestCase
from django.urls import reverse

from apps.crm_demo.models import Contact

User = get_user_model()


class ContactViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.staff_user = User.objects.create_user(
            username="staff_test",
            email="staff@test.com",
            password="testpass123",
            is_staff=True,
        )

    def test_contact_list_requires_staff(self):
        """Unauthenticated users are redirected."""
        url = reverse("crm_contact_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_contact_create_post_creates_contact(self):
        """POST to create returns 204 + HX-Trigger and creates the Contact."""
        self.client.login(username="staff_test", password="testpass123")
        url = reverse("crm_contact_create")
        data = {
            "name": "Laura",
            "email": "laura@test.com",
            "phone": "",
            "company": "ACME",
            "status": "lead",
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 204)
        self.assertIn("HX-Trigger", response)
        trigger = json.loads(response["HX-Trigger"])
        self.assertIn("showToast", trigger)
        self.assertTrue(Contact.objects.filter(email="laura@test.com").exists())

    def test_contact_inline_edit_patch(self):
        """PATCH updates the field in DB and returns HX-Trigger header."""
        self.client.login(username="staff_test", password="testpass123")
        contact = Contact.objects.create(name="Test", email="test@test.com", phone="")
        url = reverse("crm_contact_inline_edit", kwargs={"pk": contact.pk})

        mock_response = HttpResponse("<div>updated</div>", status=200)
        mock_response["HX-Trigger"] = json.dumps({"showToast": {"type": "success", "title": "Guardado", "body": ""}})

        with patch("apps.crm_demo.views.render", return_value=mock_response):
            response = self.client.patch(
                url,
                data=json.dumps({"field": "phone", "value": "123456789", "field_type": "text"}),
                content_type="application/json",
            )

        self.assertEqual(response.status_code, 200)
        self.assertIn("HX-Trigger", response)
        contact.refresh_from_db()
        self.assertEqual(contact.phone, "123456789")

    def test_contact_inline_edit_rejects_unknown_fields(self):
        """PATCH with non-allowed field returns 400 without modifying DB."""
        self.client.login(username="staff_test", password="testpass123")
        contact = Contact.objects.create(name="Test2", email="test2@test.com")
        url = reverse("crm_contact_inline_edit", kwargs={"pk": contact.pk})
        response = self.client.patch(
            url,
            data=json.dumps({"field": "email", "value": "hacked@evil.com", "field_type": "text"}),
            content_type="application/json",
        )
        self.assertEqual(response.status_code, 400)

    def test_contact_delete(self):
        """POST to delete removes the contact and returns HX-Redirect."""
        self.client.login(username="staff_test", password="testpass123")
        contact = Contact.objects.create(name="Delete Me", email="del@test.com")
        url = reverse("crm_contact_delete", kwargs={"pk": contact.pk})
        response = self.client.post(url)
        self.assertEqual(response.status_code, 204)
        self.assertIn("HX-Redirect", response)
        self.assertFalse(Contact.objects.filter(pk=contact.pk).exists())

    def test_contact_counts_returns_number(self):
        """counts endpoint returns a plain integer string."""
        self.client.login(username="staff_test", password="testpass123")
        Contact.objects.create(name="Lead1", email="lead1@test.com", status="lead")
        Contact.objects.create(name="Lead2", email="lead2@test.com", status="lead")
        url = reverse("crm_contact_counts")
        response = self.client.get(url + "?status=lead")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.content.decode(), "2")
