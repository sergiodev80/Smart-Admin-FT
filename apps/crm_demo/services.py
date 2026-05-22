import logging
from decimal import Decimal

from django.utils.translation import gettext_lazy as _

from apps.config.services import ConfigService
from apps.notifications.services import NotificationService

from .models import Contact, Purchase

logger = logging.getLogger(__name__)


class ContactService:
    @staticmethod
    def create(data: dict, created_by) -> Contact:
        current_count = Contact.objects.count()
        max_contacts = ConfigService.get("crm_demo_contact_max", default=500)
        if current_count >= max_contacts:
            raise ValueError(
                f"Se alcanzó el máximo de {max_contacts} contactos permitidos en la demo."
            )

        contact = Contact.objects.create(
            name=data["name"],
            email=data["email"],
            phone=data.get("phone", ""),
            company=data.get("company", ""),
            status=data.get("status", Contact.STATUS_LEAD),
        )

        NotificationService.send(
            user=created_by,
            title=str(_("Nuevo contacto creado")),
            body=str(_("Se creó el contacto %(name)s (%(email)s).") % {
                "name": contact.name, "email": contact.email
            }),
            channels=["in_app"],
        )
        return contact

    @staticmethod
    def register_purchase(contact: Contact, data: dict, created_by) -> Purchase:
        purchase = Purchase.objects.create(
            contact=contact,
            amount=Decimal(str(data["amount"])),
            description=data["description"],
            date=data["date"],
        )

        NotificationService.send(
            user=created_by,
            title=str(_("Nueva compra registrada")),
            body=str(_("%(name)s realizó una compra de $%(amount)s.") % {
                "name": contact.name, "amount": purchase.amount
            }),
            channels=["email"],
        )
        return purchase
