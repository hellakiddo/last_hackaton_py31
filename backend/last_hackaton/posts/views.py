from http import HTTPStatus

from asgiref.sync import async_to_sync
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Group, Post, Comment, Follow, GroupSubscription, Feed
from .permissions import IsAuthorAdminOrReadOnly
from .serializers import (
    GroupSerializer,
    PostSerializer,
    CommentSerializer, FollowSerializer,
    GroupSubscriptionSerializer, FeedSerializer
)

from users.serializers import UserSerializer


class GroupViewSet(viewsets.ModelViewSet):
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = (IsAuthorAdminOrReadOnly, )

    @action(detail=True, methods=('post',))
    def follow_group(self, request, id):
        group = self.get_object()
        serializer = GroupSubscriptionSerializer(
            data={'user': request.user.id, 'group': group.id}
        )
        serializer.save()
        return Response(serializer.data, status=HTTPStatus.CREATED)

    @action(detail=True, methods=('delete',))
    def unfollow_group(self, request, id):
        group = self.get_object()
        subscription = GroupSubscription.objects.filter(
            user=request.user, group=group
        )
        if subscription:
            subscription.delete()
            return Response(status=HTTPStatus.NO_CONTENT)
        return Response(
            {'detail': 'Вы не участник сообщества.'},
            status=HTTPStatus.NOT_FOUND
        )

    @action(detail=False, methods=('post',))
    def create_group(self, request):
        serializer = GroupSerializer(data=request.data)
        if serializer.is_valid():
            group = serializer.save(owner=request.user)
            return Response(serializer.data, status=HTTPStatus.CREATED)
        return Response(serializer.errors, status=HTTPStatus.BAD_REQUEST)

    @action(detail=True, methods=('delete',))
    def delete_group(self, request, id):
        instance = self.get_object()
        if request.user == instance.owner:
            self.perform_destroy(instance)
            return Response(status=HTTPStatus.NO_CONTENT)
        else:
            return Response(
                {'detail': 'Вы не владелец группы.'},
                status=HTTPStatus.FORBIDDEN
            )


class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    permission_classes = (IsAuthenticated, IsAuthorAdminOrReadOnly,)

    @action(detail=True, methods=('post', ))
    def create_comment(self, request, id):
        post = self.get_object()
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(post=post, author=request.user)
            return Response(serializer.data, status=HTTPStatus.CREATED)
        return Response(serializer.errors, status=HTTPStatus.BAD_REQUEST)

    @action(detail=True, methods=('delete',))
    def delete_comment(self, request, pk=None):
        comment = Comment.objects.get(pk=pk)
        comment.delete()
        return Response(status=HTTPStatus.NO_CONTENT)


class FollowViewSet(viewsets.ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    permission_classes = (IsAuthenticated,)

    @action(detail=True, methods=('post',))
    def follow(self, request, id):
        user_to_follow = self.get_object().author
        serializer = FollowSerializer(
            data={
                'user': request.user.id, 'author': user_to_follow.id}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=HTTPStatus.CREATED)
        return Response(serializer.errors, status=HTTPStatus.BAD_REQUEST)

    @action(detail=True, methods=('delete', ))
    def unfollow(self):
        follow_instance = self.get_object()
        follow_instance.delete()
        return Response(status=HTTPStatus.NO_CONTENT)


class AsyncFeedViewSet(viewsets.ModelViewSet):
    """Понимаю это ничего не сделает, просто тренируюсь для FastAPI."""
    serializer_class = FeedSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ('get',)

    async def async_get_queryset(self):
        user = self.request.user
        queryset = Feed.objects.all().filter(user=user)
        return queryset

    @async_to_sync
    async def get_queryset(self):
        return await self.async_get_queryset()
