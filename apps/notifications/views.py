from django.contrib.admin.views.decorators import staff_member_required
from django.http import HttpResponseForbidden
from django.shortcuts import render
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from .models import Notification


def _require_htmx(request):
    if not request.htmx:
        return HttpResponseForbidden()
    return None


@staff_member_required
@require_GET
def unread_count_view(request):
    if err := _require_htmx(request):
        return err
    count = Notification.objects.filter(
        recipient=request.user,
        channel=Notification.Channel.IN_APP,
        read_at__isnull=True,
    ).count()
    return render(request, "partials/notifications_badge.html", {"count": count})


@staff_member_required
@require_GET
def unread_list_view(request):
    if err := _require_htmx(request):
        return err
    notifications = Notification.objects.filter(
        recipient=request.user,
        channel=Notification.Channel.IN_APP,
        read_at__isnull=True,
    ).order_by("-created_at")[:10]
    return render(request, "partials/notifications_list.html", {"notifications": notifications})


@staff_member_required
@require_POST
def mark_read_view(request):
    if err := _require_htmx(request):
        return err
    Notification.objects.filter(
        recipient=request.user,
        channel=Notification.Channel.IN_APP,
        read_at__isnull=True,
    ).update(read_at=timezone.now())
    return render(request, "partials/notifications_badge.html", {"count": 0})
