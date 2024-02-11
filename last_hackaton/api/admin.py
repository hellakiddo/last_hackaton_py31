from django.contrib import admin
from django.utils.safestring import mark_safe

from like.models import Like
from posts.models import (
    Group, GroupSubscription,
    Hashtag, Post, Comment, Feed
)
from users.models import User, Profile, Follow
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

@admin.register(Feed)
class FeedAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'group_post')

admin.site.register(Like)