class AuditMixin:
    """
    Mix into any unfold.admin.ModelAdmin to automatically log create/update/delete
    actions to AuditLog.

    Usage:
        class MyModelAdmin(AuditMixin, ModelAdmin):
            ...
    """

    def _get_changes(self, original, form):
        if original is None:
            return None
        changes = {}
        for field, new_value in form.cleaned_data.items():
            old_value = getattr(original, field, None)
            if str(old_value) != str(new_value):
                changes[field] = {
                    "before": str(old_value),
                    "after": str(new_value),
                }
        return changes or None

    def save_model(self, request, obj, form, change):
        from apps.audit.models import AuditLog

        original = None
        if change and obj.pk:
            try:
                original = obj.__class__.objects.get(pk=obj.pk)
            except obj.__class__.DoesNotExist:
                pass

        super().save_model(request, obj, form, change)

        action = AuditLog.Action.UPDATE if change else AuditLog.Action.CREATE
        AuditLog.objects.create(
            user=request.user,
            action=action,
            model_name=f"{obj._meta.app_label}.{obj._meta.model_name}",
            object_id=str(obj.pk),
            object_repr=str(obj),
            changes=self._get_changes(original, form),
            ip_address=request.META.get("REMOTE_ADDR"),
            user_agent=request.META.get("HTTP_USER_AGENT", "")[:300],
        )

    def delete_model(self, request, obj):
        from apps.audit.models import AuditLog

        AuditLog.objects.create(
            user=request.user,
            action=AuditLog.Action.DELETE,
            model_name=f"{obj._meta.app_label}.{obj._meta.model_name}",
            object_id=str(obj.pk),
            object_repr=str(obj),
            ip_address=request.META.get("REMOTE_ADDR"),
            user_agent=request.META.get("HTTP_USER_AGENT", "")[:300],
        )
        super().delete_model(request, obj)
