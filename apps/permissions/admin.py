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
    list_display_links = ("name",)
    search_fields = ("name", "description")
    filter_horizontal = ("permissions",)
    compressed_fields = True
    warn_unsaved_change = True

    @admin.display(description=_("usuarios"))
    def user_count(self, obj):
        return obj.user_roles.count()


@admin.register(UserRole)
class UserRoleAdmin(ModelAdmin):
    list_display = ("user", "role", "assigned_by", "assigned_at")
    list_display_links = ("user",)
    list_filter = ("role",)
    search_fields = ("user__username", "role__name")
    readonly_fields = ("assigned_at",)
    compressed_fields = True
    warn_unsaved_change = True


@admin.register(ObjectPermission)
class ObjectPermissionAdmin(ModelAdmin):
    list_display = ("user", "content_type", "object_id", "permission")
    list_display_links = ("user",)
    list_filter = ("content_type",)
    search_fields = ("user__username", "object_id")
    warn_unsaved_change = True
