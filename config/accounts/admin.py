from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        (
            "Professional profile",
            {"fields": ("profile_picture", "headline", "bio", "location", "website")},
        ),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ("Contact", {"fields": ("email", "first_name", "last_name")}),
    )
    list_display = ("email", "username", "first_name", "last_name", "is_staff")
    ordering = ("email",)
