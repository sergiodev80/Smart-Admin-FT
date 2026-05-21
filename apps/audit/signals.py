from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver


def _get_ip(request):
    x_forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded:
        return x_forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR")


@receiver(user_logged_in)
def on_login(sender, request, user, **kwargs):
    from apps.audit.models import AuditLog
    AuditLog.objects.create(
        user=user,
        action=AuditLog.Action.LOGIN,
        model_name="",
        object_repr=str(user),
        ip_address=_get_ip(request),
        user_agent=request.META.get("HTTP_USER_AGENT", "")[:300],
    )


@receiver(user_logged_out)
def on_logout(sender, request, user, **kwargs):
    from apps.audit.models import AuditLog
    AuditLog.objects.create(
        user=user,
        action=AuditLog.Action.LOGOUT,
        model_name="",
        object_repr=str(user) if user else "",
        ip_address=_get_ip(request),
        user_agent=request.META.get("HTTP_USER_AGENT", "")[:300],
    )
