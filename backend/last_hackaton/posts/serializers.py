from django.core.exceptions import ValidationError
from rest_framework import serializers
from drf_base64.fields import Base64ImageField

from .models import Group, Post, Comment, GroupSubscription

class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('title', 'slug', 'description', 'image')

    def validate_slug(self, value):
        """Валидация уникальности слага при создании группы."""
        if Group.objects.filter(slug=value).exists():
            raise serializers.ValidationError("Группа с таким слагом уже существует.")
        return value

    def validate_title(self, value):
        """Валидация уникальности заголовка при создании группы."""
        if Group.objects.filter(title=value).exists():
            raise serializers.ValidationError("Группа с таким заголовком уже существует.")
        return value


class CommentSerializer(serializers.ModelSerializer):
    """Комменты."""
    author_username = serializers.ReadOnlyField(source='author.username')

    class Meta:
        model = Comment
        fields = (
            'id', 'post', 'author_username', 'text', 'pub_date', 'parent_comment'
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

    def to_representation(self, instance):
        return {
            'message': f'Вы подписались на группу - {instance.group.title}',
        }
    def validate(self, data):
        user = data['user']
        group = data['group']
        if GroupSubscription.objects.all().filter(
                user=user, group=group
        ).exists():
            raise ValidationError('Вы уже подписаны на данную группу.')
        return data

class FeedSerializer(serializers.ModelSerializer):
    """Лента - Посты групп и пользователей на которых подписан автор."""
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

