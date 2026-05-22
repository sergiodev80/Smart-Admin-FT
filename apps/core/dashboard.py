import json
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.db.models import Count
from django.db.models.functions import TruncDate
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

User = get_user_model()


def _get_crm_cards_safe(request):
    try:
        from apps.crm_demo.dashboard import get_crm_cards
        return get_crm_cards(request)
    except Exception:
        return []


class _Table:
    """Objeto mínimo compatible con el componente table de Unfold."""
    def __init__(self, headers, rows):
        self.headers = headers
        self.rows = rows


def _audit_chart_data() -> dict:
    from apps.audit.models import AuditLog
    today = timezone.now().date()
    days = [today - timedelta(days=i) for i in range(6, -1, -1)]
    counts = {
        row["day"]: row["total"]
        for row in AuditLog.objects.filter(
            timestamp__date__gte=days[0]
        ).annotate(day=TruncDate("timestamp")).values("day").annotate(total=Count("id"))
    }
    day_names = [_("Lun"), _("Mar"), _("Mié"), _("Jue"), _("Vie"), _("Sáb"), _("Dom")]
    return {
        "labels": [str(day_names[d.weekday()]) for d in days],
        "datasets": [{
            "label": str(_("Actividad")),
            "data": [counts.get(d, 0) for d in days],
            "backgroundColor": "var(--color-primary-500)",
            "borderRadius": 4,
        }],
    }


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
            *_get_crm_cards_safe(request),
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
        "chart_data": json.dumps(_audit_chart_data()),
    })
    return context
