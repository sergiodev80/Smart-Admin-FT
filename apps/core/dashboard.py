from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

User = get_user_model()


def dashboard_callback(request, context):
    """
    Inyecta datos de widgets en el contexto del dashboard de Unfold.

    PROYECTO: Para personalizar, copia esta función a tu app y actualiza
    UNFOLD["DASHBOARD_CALLBACK"] en config/settings/base.py para apuntar a ella.
    Agrega las claves que necesites a context.update({...}).
    """
    from apps.audit.models import AuditLog
    from apps.notifications.models import Notification

    today = timezone.now().date()

    total_users = User.objects.count()
    unread_notifications = Notification.objects.filter(
        recipient=request.user,
        channel="in_app",
        read_at__isnull=True,
    ).count()
    audit_today = AuditLog.objects.filter(timestamp__date=today).count()

    context.update({
        "stat_cards": [
            {
                "title": _("Usuarios"),
                "value": total_users,
                "icon": "group",
                "description": _("Total registrados"),
            },
            {
                "title": _("Notificaciones"),
                "value": unread_notifications,
                "icon": "notifications",
                "description": _("Sin leer"),
            },
            {
                "title": _("Auditoría hoy"),
                "value": audit_today,
                "icon": "history",
                "description": _("Registros de hoy"),
            },
        ],
        "recent_users": User.objects.order_by("-date_joined")[:5],
        "recent_audit": AuditLog.objects.order_by("-timestamp")[:5],
    })
    return context
