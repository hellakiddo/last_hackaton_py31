from http import HTTPStatus

from django.core.exceptions import ValidationError
from rest_framework.serializers import SerializerMethodField, ModelSerializer
from rest_framework import serializers

from .models import User, Profile, Follow
from posts.serializers import (
    PostSerializer, GroupSerializer,
    GroupSubscriptionSerializer
)


class UserSerializer(ModelSerializer):
    """Сериалайзер для создания и получение списка пользователей."""
    password = serializers.CharField(min_length=8, required=True, write_only=True)
    password_confirm = serializers.CharField(min_length=8, required=True, write_only=True)
    class Meta:
        model = User
        fields = (
            'email',
            'username',
            'password',
            'password_confirm',
            'first_name',
            'last_name',
            "date_of_birth",
        )

        ref_name = 'UserSerializerUsersApp'

    def validate(self, attrs):
        password = attrs.get('password')
        password_to_confirm = attrs.pop('password_confirm')
        if password != password_to_confirm:
            raise serializers.ValidationError('Пароли не совпадают.')
        return attrs

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class LogOutSerialzer(serializers.Serializer):
    """Логаут."""
    refresh = serializers.CharField(required=True, write_only=True)

class FollowSerializer(ModelSerializer):
    """Подписки на пользователей."""

    class Meta:
        model = Follow
        fields = ('id', 'user', 'author')

    def validate(self, data):
        user = data['user']
        author = data['author']

        if Follow.objects.filter(user=user, author=author).exists():
            raise ValidationError(
                "Вы уже подписаны на этого автора"
            )
        if user == author:
            raise ValidationError(
                "Подписаться на самого себя невозможно",
                code=HTTPStatus.BAD_REQUEST,
            )
        return data


class ProfileSerializer(ModelSerializer):
    """Профиль пользователя."""
    posts = PostSerializer(many=True, read_only=True)
    subscriptions = SerializerMethodField()
    subscribers = SerializerMethodField()
    is_subscribed = SerializerMethodField()

    class Meta:
        model = Profile
        fields = (
            'id',
            'bio',
            'icon',
            'posts',
            'subscriptions',
            'subscribers',
            'is_subscribed',
        )

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        user_posts = instance.user.posts.all()
        post_serializer = PostSerializer(user_posts, many=True)
        representation['user_posts'] = post_serializer.data
        representation['username'] = instance.user.username

        return representation

    def get_subscriptions(self, instance):
        subscriptions = instance.user.follower.all()
        subscription_serializer = FollowSerializer(subscriptions, many=True)
        return subscription_serializer.data

    def get_subscribers(self, instance):
        subscribers = instance.user.following.all()
        subscriber_serializer = FollowSerializer(subscribers, many=True)
        return subscriber_serializer.data

    def get_is_subscribed(self, obj):
        request = self.context.get("request")
        return (request.user.is_authenticated
                and request.user.follower.filter(author=obj.user).exists())
