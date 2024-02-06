from rest_framework import serializers
from drf_base64.fields import Base64ImageField

from .models import Group, Post, Comment, GroupSubscription

class GroupSerializer(serializers.ModelSerializer):
    image = Base64ImageField()
    class Meta:
        model = Group
        fields = ('title', 'slug', 'description', 'image')

class CommentSerializer(serializers.ModelSerializer):
    """Комменты."""

    class Meta:
        model = Comment
        fields = (
            'id', 'post', 'author', 'text', 'pub_date', 'parent_comment'
        )

class PostSerializer(serializers.ModelSerializer):
    """Посты."""
    image = Base64ImageField()
    comments = CommentSerializer(many=True, read_only=True)
    author_username = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = Post
        fields = (
            'id',
            'text',
            'pub_date',
            'author',
            'author_username',
            'group',
            'image',
            'video',
            'parent_post',
            'comments'
        )

    def validate_image(self, image):
        supported_formats = ["jpg", "jpeg", "png"]
        file_extension = image.name.split('.')[-1]
        if not image:
            raise serializers.ValidationError(
                {'image': "Нужна картинка."}
            )
        if file_extension.lower() not in supported_formats:
            raise serializers.ValidationError(
                {'file_extension': "Непонятный формат картинки."}
            )
        return image


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
    """Лента - Посты групп и пользователей на которых подписан автор."""
    image = Base64ImageField()
    username = serializers.SerializerMethodField()
    hashtags = serializers.SerializerMethodField()
    comments = CommentSerializer(many=True, read_only=True)
    class Meta:
        model = Post
        fields = '__all__'

    def get_username(self, obj):
        return obj.author.username

    def get_hashtags(self, obj):
        return [hashtag.name for hashtag in obj.hashtags.all()]