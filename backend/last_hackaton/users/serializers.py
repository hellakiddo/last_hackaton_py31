from rest_framework import serializers

from .models import User, Profile
from posts.serializers import (
    PostSerializer, GroupSerializer,
    FollowSerializer, GroupSubscriptionSerializer
)
from posts.models import GroupSubscription, Follow


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


class ProfileSerializer(serializers.ModelSerializer):
    posts = PostSerializer(many=True, read_only=True)
    subscriptions = serializers.SerializerMethodField()
    subscriptions_groups = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = (
            'id',
            'bio',
            'icon',
            'posts',
            'subscriptions',
            'subscriptions_groups'
        )

    def get_subscriptions(self, obj):
        subscriptions = Follow.objects.filter(user=obj)
        serializer = FollowSerializer(subscriptions, many=True)
        return serializer.data

    def get_subscriptions_groups(self, obj):
        groups = GroupSubscription.objects.filter(user=obj)
        serializer = GroupSubscriptionSerializer(groups, many=True)
        return serializer.data
