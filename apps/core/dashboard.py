import json

from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

User = get_user_model()


class _Table:
    """Objeto mínimo compatible con el componente table de Unfold."""
    def __init__(self, headers, rows):
        self.headers = headers
        self.rows = rows


def dashboard_callback(request, context):
    """
    Inyecta datos de widgets en el contexto del dashboard de Unfold.

    PROYECTO: Para personalizar, copia esta función a tu app y actualiza
    UNFOLD["DASHBOARD_CALLBACK"] en config/settings/base.py para apuntar a ella.
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

    recent_users_qs = User.objects.order_by("-date_joined")[:5]
    recent_audit_qs = AuditLog.objects.order_by("-timestamp")[:5]

    context.update({
        "stat_cards": [
            {"title": _("Usuarios"), "value": total_users, "icon": "group", "description": _("Total registrados")},
            {"title": _("Notificaciones"), "value": unread_notifications, "icon": "notifications", "description": _("Sin leer")},
            {"title": _("Auditoría hoy"), "value": audit_today, "icon": "history", "description": _("Registros de hoy")},
            # PROYECTO: agregar stat cards específicas del proyecto aquí
        ],
        "users_table": _Table(
            headers=[_("Usuario"), _("Email"), _("Registrado")],
            rows=[
                [u.username, u.email or "—", u.date_joined.strftime("%d/%m/%y")]
                for u in recent_users_qs
            ],
        ),
        "audit_table": _Table(
            headers=[_("Acción"), _("Modelo"), _("Fecha")],
            rows=[
                [log.get_action_display(), log.model_name, log.timestamp.strftime("%d/%m %H:%M")]
                for log in recent_audit_qs
            ],
        ),
        # PROYECTO: reemplaza con datos reales. Formato Chart.js estándar.
        "chart_data": json.dumps({
            "labels": ["Lun", "Mar", "Mié", "Jue", "Vie", "Sáb", "Dom"],
            "datasets": [{
                "label": "Actividad",
                "data": [12, 19, 8, 15, 22, 6, 10],
                "backgroundColor": "var(--color-primary-500)",
                "borderRadius": 4,
            }],
        }),
    })
    return context
