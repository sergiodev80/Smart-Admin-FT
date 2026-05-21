from django.contrib import admin
from django.contrib.auth.models import Group
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin, TabularInline

from .models import ObjectPermission, Role, UserRole

# Role replaces Group when this app is active — hide the built-in Group from admin.
admin.site.unregister(Group)


class UserRoleInline(TabularInline):
    model = UserRole
    extra = 0
    fields = ("role", "assigned_by", "assigned_at")
    readonly_fields = ("assigned_at",)
    verbose_name = _("rol asignado")
    verbose_name_plural = _("roles asignados")


@admin.register(Role)
class RoleAdmin(ModelAdmin):
    list_display = ("name", "description", "user_count")
    search_fields = ("name", "description")
    filter_horizontal = ("permissions",)

    @admin.display(description=_("usuarios"))
    def user_count(self, obj):
        return obj.user_roles.count()


@admin.register(UserRole)
class UserRoleAdmin(ModelAdmin):
    list_display = ("user", "role", "assigned_by", "assigned_at")
    list_filter = ("role",)
    search_fields = ("user__username", "role__name")
    readonly_fields = ("assigned_at",)


@admin.register(ObjectPermission)
class ObjectPermissionAdmin(ModelAdmin):
    list_display = ("user", "content_type", "object_id", "permission")
    list_filter = ("content_type",)
    search_fields = ("user__username", "object_id")
