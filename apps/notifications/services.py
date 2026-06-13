import hashlib
import hmac
import json
import logging
import time
from datetime import datetime, timezone

import requests
from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger(__name__)


class NotificationService:
    @staticmethod
    def send(user, title: str, body: str, channels: list, payload: dict = None) -> None:
        payload = payload or {}
        for channel in channels:
            try:
                if channel == "in_app":
                    NotificationService._send_in_app(user, title, body, payload)
                elif channel == "email":
                    NotificationService._send_email(user, title, body)
                elif channel == "webhook":
                    NotificationService._send_webhook(user, title, body, payload)
            except Exception as e:
                logger.error(
                    "NotificationService error on channel %s for user %s: %s",
                    channel, user, e,
                )

    @staticmethod
    def _send_in_app(user, title, body, payload):
        from apps.notifications.models import Notification
        Notification.objects.create(
            recipient=user,
            title=title,
            body=body,
            channel="in_app",
            payload=payload,
            sent_at=datetime.now(tz=timezone.utc),
        )

    @staticmethod
    def _send_email(user, title, body):
        from apps.notifications.models import Notification
        send_mail(
            subject=title,
            message=body,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            fail_silently=False,
        )
        Notification.objects.create(
            recipient=user,
            title=title,
            body=body,
            channel="email",
            sent_at=datetime.now(tz=timezone.utc),
        )

    @staticmethod
    def _send_webhook(user, title, body, payload):
        from apps.notifications.models import Notification, WebhookEndpoint
        endpoints = WebhookEndpoint.objects.filter(user=user, is_active=True)
        for endpoint in endpoints:
            data = {"title": title, "body": body, **payload}
            body_bytes = json.dumps(data).encode("utf-8")
            signature = hmac.new(
                endpoint.secret.encode("utf-8"),
                body_bytes,
                hashlib.sha256,
            ).hexdigest()
            headers = {
                "Content-Type": "application/json",
                "X-Signature": f"sha256={signature}",
            }
            delivered = False
            for attempt, delay in enumerate([0, 1, 2, 4], start=1):
                if delay:
                    time.sleep(delay)
                try:
                    requests.post(endpoint.url, data=body_bytes, headers=headers, timeout=5)
                    delivered = True
                    break
                except requests.RequestException as e:
                    logger.warning(
                        "Webhook POST attempt %d/4 failed to %s: %s",
                        attempt, endpoint.url, e,
                    )
            if delivered:
                Notification.objects.create(
                    recipient=user,
                    title=title,
                    body=body,
                    channel="webhook",
                    payload=payload,
                    sent_at=datetime.now(tz=timezone.utc),
                )
            else:
                logger.error("Webhook delivery failed after 4 attempts to %s", endpoint.url)
