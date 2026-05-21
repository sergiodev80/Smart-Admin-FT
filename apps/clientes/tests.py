from django.test import TestCase
from apps.clientes.models import Cliente


class ClienteModelTest(TestCase):
    def test_default_estado_is_activo(self):
        cliente = Cliente(nombre="Acme", email="acme@test.com")
        self.assertEqual(cliente.estado, "activo")

    def test_str_returns_nombre(self):
        cliente = Cliente(nombre="Acme Corp", email="acme@test.com")
        self.assertEqual(str(cliente), "Acme Corp")
