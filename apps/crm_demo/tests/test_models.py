from django.db import IntegrityError
from django.test import TestCase

from apps.crm_demo.models import Contact, SocialProfile


class ContactModelTest(TestCase):
    def test_status_default_is_lead(self):
        contact = Contact.objects.create(name="Ana", email="ana@test.com")
        self.assertEqual(contact.status, "lead")

    def test_valid_status_choices(self):
        for status in ("lead", "prospect", "client", "inactive"):
            c = Contact.objects.create(name="X", email=f"{status}@test.com", status=status)
            self.assertEqual(c.status, status)

    def test_social_profile_unique_per_network(self):
        contact = Contact.objects.create(name="Bob", email="bob@test.com")
        SocialProfile.objects.create(contact=contact, network="linkedin", url="https://linkedin.com/in/bob")
        with self.assertRaises(IntegrityError):
            SocialProfile.objects.create(contact=contact, network="linkedin", url="https://linkedin.com/in/bob2")
