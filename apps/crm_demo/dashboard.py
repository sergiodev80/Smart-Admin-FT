from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.core.dashboard import _Table


def get_crm_cards(request):
    from .models import CallLog, Contact, EmailLog, Purchase

    today = timezone.now().date()
    this_month = timezone.now().replace(day=1).date()

    return [
        {
            "title": str(_("Contactos totales")),
            "value": Contact.objects.count(),
            "icon": "contacts",
            "description": str(_("Registrados en el sistema")),
        },
        {
            "title": str(_("Compras este mes")),
            "value": Purchase.objects.filter(date__gte=this_month).count(),
            "icon": "shopping_cart",
            "description": str(_("Desde el 1 del mes")),
        },
        {
            "title": str(_("Llamadas hoy")),
            "value": CallLog.objects.filter(date__date=today).count(),
            "icon": "call",
            "description": str(_("Del día de hoy")),
        },
        {
            "title": str(_("Emails hoy")),
            "value": EmailLog.objects.filter(date__date=today).count(),
            "icon": "email",
            "description": str(_("Del día de hoy")),
        },
    ]


def get_recent_contacts_table(request):
    from .models import Contact

    recent = Contact.objects.order_by("-created_at")[:5]
    return _Table(
        headers=[str(_("Nombre")), str(_("Email")), str(_("Estado")), str(_("Creado"))],
        rows=[
            [c.name, c.email, c.get_status_display(), c.created_at.strftime("%d/%m/%y")]
            for c in recent
        ],
    )
