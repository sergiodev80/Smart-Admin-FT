from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from unfold.admin import ModelAdmin

from .models import User


@admin.register(User)
class UserAdmin(ModelAdmin, BaseUserAdmin):
    list_display = ("username", "email", "role", "is_staff", "is_active", "erp_employee_id")
    list_display_links = ("username",)
    list_filter = ("role", "is_staff", "is_active")
    search_fields = ("username", "email", "erp_employee_id")
    compressed_fields = True
    warn_unsaved_change = True
    fieldsets = BaseUserAdmin.fieldsets + (
        ("Información adicional", {"fields": ("role", "erp_employee_id")}),
    )
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ("Información adicional", {"fields": ("role", "erp_employee_id")}),
    )
