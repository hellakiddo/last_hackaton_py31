from django.contrib import admin
from django.utils.safestring import mark_safe

from posts.models import (
    Group, GroupSubscription,
    Hashtag, Post, Comment,
    Follow, Feed
)
from users.models import User, Profile
@admin.register(Group)
class GroupAdmin(admin.ModelAdmin):
    list_display = ('title', 'owner', 'image_display')
    search_fields = ('title', 'owner__username')

    def image_display(self, obj):
        return obj.image.url if obj.image else None

    image_display.short_description = 'Image'

@admin.register(GroupSubscription)
class GroupSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'group')

@admin.register(Hashtag)
class HashtagAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('text', 'pub_date', 'author', 'group', 'image_display')
    search_fields = ('text', 'author__username')

    def image_display(self, obj):
        return obj.image.url if obj.image else None

    image_display.short_description = 'Image'

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author', 'text', 'pub_date')
    search_fields = ('text', 'author__username')

@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('user', 'author')

@admin.register(Feed)
class FeedAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'group_post')

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
