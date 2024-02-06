from http import HTTPStatus

from django.core.exceptions import ValidationError
from rest_framework import serializers

from .models import User, Profile, Follow
from posts.serializers import (
    PostSerializer, GroupSerializer,
    GroupSubscriptionSerializer
)
from posts.models import GroupSubscription


class UserSerializer(serializers.ModelSerializer):
    """Сериалайзер для создания и получение списка пользователей."""
    class Meta:
        model = User
        fields = (
            "email",
            "id",
            "username",
            "first_name",
            "last_name",
            "date_of_birth",
        )

        ref_name = 'UserSerializerUsersApp'


class FollowSerializer(serializers.ModelSerializer):

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


class ProfileSerializer(serializers.ModelSerializer):
    posts = PostSerializer(many=True, read_only=True)
    subscriptions = serializers.SerializerMethodField()
    subscribers = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = (
            'id',
            'bio',
            'icon',
            'posts',
            'subscriptions',
            'subscribers',
        )

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        user_posts = instance.user.posts.all()
        post_serializer = PostSerializer(user_posts, many=True)
        representation['user_posts'] = post_serializer.data

        return representation

    def get_subscriptions(self, instance):
        subscriptions = instance.user.follower.all()
        subscription_serializer = FollowSerializer(subscriptions, many=True)
        return subscription_serializer.data

    def get_subscribers(self, instance):
        subscribers = instance.user.following.all()
        subscriber_serializer = FollowSerializer(subscribers, many=True)
        return subscriber_serializer.data

