from django.test import TestCase, RequestFactory
from django.urls import reverse
from unittest.mock import patch

from .backends import EmailOrUsernameBackend
from .models import User


class UserModelTest(TestCase):
    def test_str_includes_username(self):
        user = User.objects.create_user(username="u1", password="pass")
        self.assertIn("u1", str(user))

    def test_erp_employee_id_optional(self):
        user = User.objects.create_user(username="u2", password="pass")
        self.assertIsNone(user.erp_employee_id)

    def test_erp_employee_id_can_be_set(self):
        user = User.objects.create_user(
            username="u3", password="pass", erp_employee_id="EMP001"
        )
        self.assertEqual(user.erp_employee_id, "EMP001")


class EmailOrUsernameBackendTest(TestCase):
    def setUp(self):
        self.backend = EmailOrUsernameBackend()
        self.user = User.objects.create_user(
            username="testuser",
            email="test@solid.com.py",
            password="testpass123",
        )

    def test_login_with_username(self):
        user = self.backend.authenticate(None, username="testuser", password="testpass123")
        self.assertEqual(user, self.user)

    def test_login_with_email(self):
        user = self.backend.authenticate(None, username="test@solid.com.py", password="testpass123")
        self.assertEqual(user, self.user)

    def test_wrong_password_returns_none(self):
        user = self.backend.authenticate(None, username="testuser", password="wrong")
        self.assertIsNone(user)

    def test_nonexistent_user_returns_none(self):
        user = self.backend.authenticate(None, username="noexiste", password="pass")
        self.assertIsNone(user)

    def test_no_username_returns_none(self):
        user = self.backend.authenticate(None, username=None, password="pass")
        self.assertIsNone(user)

    def test_inactive_user_returns_none(self):
        self.user.is_active = False
        self.user.save()
        user = self.backend.authenticate(None, username="testuser", password="testpass123")
        self.assertIsNone(user)


class SolicitarAccesoViewTest(TestCase):
    def test_get_returns_200(self):
        response = self.client.get(reverse("request_access"))
        self.assertEqual(response.status_code, 200)

    def test_email_ya_existente(self):
        User.objects.create_user(username="existing@solid.com.py", email="existing@solid.com.py", password="pass")
        response = self.client.post(reverse("request_access"), {"email": "existing@solid.com.py"})
        self.assertContains(response, "Ya existe una cuenta")

    @patch("apps.core.views.ERPUserService.find_by_email", return_value=None)
    def test_email_no_en_erp(self, mock_erp):
        response = self.client.post(reverse("request_access"), {"email": "nuevo@solid.com.py"})
        self.assertContains(response, "no está registrado")

    @patch("apps.core.views._send_activation_email")
    @patch("apps.core.views.ERPUserService.find_by_email", return_value={"name": "Juan", "login": "jlopez"})
    def test_usuario_creado_correctamente(self, mock_erp, mock_email):
        self.client.post(reverse("request_access"), {"email": "nuevo@solid.com.py"})
        self.assertTrue(User.objects.filter(email="nuevo@solid.com.py").exists())
        user = User.objects.get(email="nuevo@solid.com.py")
        self.assertEqual(user.erp_employee_id, "jlopez")
        self.assertTrue(user.is_staff)
        self.assertTrue(user.is_active)

    @patch("apps.core.views._send_activation_email")
    @patch("apps.core.views.ERPUserService.find_by_email", return_value={"name": "Juan", "login": "jlopez"})
    def test_post_exitoso_redirige(self, mock_erp, mock_email):
        response = self.client.post(reverse("request_access"), {"email": "nuevo@solid.com.py"})
        self.assertRedirects(response, reverse("request_access"))
