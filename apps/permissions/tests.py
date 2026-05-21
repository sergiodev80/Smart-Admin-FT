from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.test import TestCase

User = get_user_model()


class RoleModelTest(TestCase):
    def test_create_role(self):
        from apps.permissions.models import Role
        role = Role.objects.create(name="editor", description="Puede editar contenido")
        self.assertEqual(str(role), "editor")

    def test_role_name_unique(self):
        from apps.permissions.models import Role
        from django.db import IntegrityError
        Role.objects.create(name="unique_role")
        with self.assertRaises(IntegrityError):
            Role.objects.create(name="unique_role")


class UserRoleTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="roleuser", password="pass")
        from apps.permissions.models import Role
        self.role = Role.objects.create(name="tester")

    def test_assign_role_to_user(self):
        from apps.permissions.models import UserRole
        ur = UserRole.objects.create(user=self.user, role=self.role)
        self.assertEqual(ur.user, self.user)
        self.assertEqual(ur.role, self.role)

    def test_user_roles_relation(self):
        from apps.permissions.models import Role, UserRole
        UserRole.objects.create(user=self.user, role=self.role)
        self.assertIn(self.role, Role.objects.filter(user_roles__user=self.user))


class ObjectPermissionTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username="objperm_user", password="pass")
        self.ct = ContentType.objects.get_for_model(User)
        from django.contrib.auth.models import Permission
        self.perm = Permission.objects.filter(content_type=self.ct).first()

    def test_create_object_permission(self):
        from apps.permissions.models import ObjectPermission
        op = ObjectPermission.objects.create(
            user=self.user,
            content_type=self.ct,
            object_id=str(self.user.pk),
            permission=self.perm,
        )
        self.assertEqual(op.user, self.user)


class PermissionsAdminRegisteredTest(TestCase):
    def test_role_registered(self):
        from django.contrib import admin
        from apps.permissions.models import Role
        self.assertIn(Role, admin.site._registry)
