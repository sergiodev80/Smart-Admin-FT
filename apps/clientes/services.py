import logging

from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)


class ClienteService:
    @staticmethod
    def notify_new_client(cliente):
        from django.contrib.auth import get_user_model
        from apps.notifications.services import NotificationService

        User = get_user_model()
        users = User.objects.filter(is_active=True)
        for user in users:
            NotificationService.send(
                user=user,
                title=str(_("Nuevo cliente registrado")),
                body=str(_("Se registró el cliente: %(nombre)s") % {"nombre": cliente.nombre}),
                channels=["in_app"],
            )
