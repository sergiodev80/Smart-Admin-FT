class AuditMiddleware:
    """
    Optional middleware — logs 'view' actions for every authenticated GET request.
    Add to MIDDLEWARE in settings only if needed:
        "apps.audit.middleware.AuditMiddleware"
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if (
            request.method == "GET"
            and request.user.is_authenticated
            and not request.path.startswith("/static/")
        ):
            from apps.audit.models import AuditLog
            x_forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
            ip = x_forwarded.split(",")[0].strip() if x_forwarded else request.META.get("REMOTE_ADDR")
            AuditLog.objects.create(
                user=request.user,
                action=AuditLog.Action.VIEW,
                model_name="",
                object_repr=request.path,
                ip_address=ip,
                user_agent=request.META.get("HTTP_USER_AGENT", "")[:300],
            )
        return response
