from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from unfold.admin import ModelAdmin

from .models import User


def _get_user_role_inline():
    try:
        from apps.permissions.admin import UserRoleInline
        return [UserRoleInline]
    except ImportError:
        return []


@admin.register(User)
class UserAdmin(ModelAdmin, BaseUserAdmin):
    list_display = ("username", "email", "is_staff", "is_active", "erp_employee_id")
    list_display_links = ("username",)
    list_filter = ("is_staff", "is_active")
    search_fields = ("username", "email", "erp_employee_id")
    compressed_fields = True
    warn_unsaved_change = True
    inlines = _get_user_role_inline()
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Información adicional", {"fields": ("erp_employee_id",)}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("Información adicional", {"fields": ("erp_employee_id",)}),
    )
