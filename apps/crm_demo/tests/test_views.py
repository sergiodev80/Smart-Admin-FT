from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from apps.crm_demo.models import Contact

User = get_user_model()


class ContactViewAccessTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.staff_user = User.objects.create_user(
            username="staff_test",
            email="staff@test.com",
            password="testpass123",
            is_staff=True,
        )

    def test_contact_list_requires_staff(self):
        url = reverse("crm_contact_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_contact_list_accessible_for_staff(self):
        self.client.login(username="staff_test", password="testpass123")
        url = reverse("crm_contact_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_contact_items_partial(self):
        self.client.login(username="staff_test", password="testpass123")
        url = reverse("crm_contact_items")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
