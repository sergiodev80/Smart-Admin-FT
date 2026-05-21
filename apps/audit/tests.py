from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class AuditLogModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="auditor", password="pass")

    def test_create_audit_log(self):
        from apps.audit.models import AuditLog
        log = AuditLog.objects.create(
            user=self.user,
            action=AuditLog.Action.CREATE,
            model_name="core.User",
            object_id="1",
            object_repr="auditor (Traductor)",
        )
        self.assertEqual(str(log), "create — core.User #1")

    def test_audit_log_without_user(self):
        from apps.audit.models import AuditLog
        log = AuditLog.objects.create(
            action=AuditLog.Action.LOGIN,
            model_name="",
            object_repr="system",
        )
        self.assertIsNone(log.user)

    def test_all_actions_valid(self):
        from apps.audit.models import AuditLog
        for action in AuditLog.Action.values:
            log = AuditLog.objects.create(
                action=action,
                model_name="test",
                object_repr="test",
            )
            self.assertEqual(log.action, action)


class AuditLoginSignalTest(TestCase):
    def test_login_creates_audit_log(self):
        from apps.audit.models import AuditLog
        User.objects.create_user(username="loginuser", password="pass")
        self.client.login(username="loginuser", password="pass")
        self.assertTrue(AuditLog.objects.filter(action=AuditLog.Action.LOGIN).exists())

    def test_logout_creates_audit_log(self):
        from apps.audit.models import AuditLog
        User.objects.create_user(username="logoutuser", password="pass")
        self.client.login(username="logoutuser", password="pass")
        self.client.logout()
        self.assertTrue(AuditLog.objects.filter(action=AuditLog.Action.LOGOUT).exists())


class AuditAdminRegisteredTest(TestCase):
    def test_auditlog_registered(self):
        from django.contrib import admin
        from apps.audit.models import AuditLog
        self.assertIn(AuditLog, admin.site._registry)
