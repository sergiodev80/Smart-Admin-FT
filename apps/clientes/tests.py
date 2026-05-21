from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.test import TestCase

from apps.clientes.models import Cliente

User = get_user_model()


class ClienteModelTest(TestCase):
    def test_default_estado_is_activo(self):
        cliente = Cliente(nombre="Acme", email="acme@test.com")
        self.assertEqual(cliente.estado, "activo")

    def test_str_returns_nombre(self):
        cliente = Cliente(nombre="Acme Corp", email="acme@test.com")
        self.assertEqual(str(cliente), "Acme Corp")


class ClienteSignalTest(TestCase):
    def test_notify_called_on_create(self):
        with patch("apps.clientes.services.ClienteService.notify_new_client") as mock_notify:
            cliente = Cliente.objects.create(nombre="Acme", email="signal@test.com")
            mock_notify.assert_called_once_with(cliente)

    def test_notify_not_called_on_update(self):
        cliente = Cliente.objects.create(nombre="Acme", email="update@test.com")
        with patch("apps.clientes.services.ClienteService.notify_new_client") as mock_notify:
            cliente.estado = "inactivo"
            cliente.save()
            mock_notify.assert_not_called()
