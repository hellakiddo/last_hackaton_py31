from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from users.models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
    )
    list_display_links = (
        "username",
        "email",
    )
    list_filter = ("username", "email")
    search_fields = ("username",)
    empty_value_display = "-пусто-"
