from rest_framework import serializers
from .models import Group, Post, Comment, Follow, GroupSubscription, Feed

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('title', 'slug', 'description')

class CommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = (
            'id', 'post', 'author', 'text', 'pub_date', 'parent_comment'
        )

class PostSerializer(serializers.ModelSerializer):
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Post
        fields = (
            'id',
            'text',
            'pub_date',
            'author',
            'group',
            'image',
            'video',
            'parent_post',
            'comments'
        )

class FollowSerializer(serializers.ModelSerializer):

    class Meta:
        model = Follow
        fields = ('id', 'user', 'author')


class GroupSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = GroupSubscription
        fields = ('user', 'group')
        read_only_fields = ('user', )

    def to_representation(self, instance):
        return {
            'group_id': instance.group.id,
            'group_title': instance.group.title,
            'user_id': instance.user.id,
            'user_username': instance.user.username,
        }

class FeedSerializer(serializers.ModelSerializer):
    post = PostSerializer()
    group_post = PostSerializer()

    class Meta:
        model = Feed
        fields = ('user', 'post', 'group_post')