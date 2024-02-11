from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import Follow, User, Profile

@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name')
    search_fields = ("username", "email")

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('get_username', 'bio', 'icon')

    def get_username(self, obj):
        return obj.user.username
    get_username.short_description = "Username"

    def icon(self, obj):
        return mark_safe(f'<img src="{obj.avatar.url}" width="50" height="50" />')

    icon.short_description = "Картинка"