from rest_framework import serializers
from .models import Like
# from posts.serializers import PostSerializer


class LikeSerializer(serializers.ModelSerializer):
    owner = serializers.ReadOnlyField(source='owner.username')

    class Meta:
        model = Like
        fields = ['owner']