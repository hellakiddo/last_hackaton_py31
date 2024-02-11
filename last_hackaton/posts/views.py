from http import HTTPStatus
from rest_framework import permissions
from django.db.models import Count

from asgiref.sync import async_to_sync
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from like.models import Like
from .models import Group, Post, Comment, GroupSubscription, Hashtag
from .permissions import IsOwnerAdminOrReadOnly, IsAuthorAdminOrReadOnly
from .serializers import (
    GroupSerializer,
    PostSerializer,
    CommentSerializer,
    GroupSubscriptionSerializer, 
    FeedSerializer, 
    HashtagSerializer
)
from users.models import Follow


class GroupViewSet(viewsets.ModelViewSet):
    """Группы."""
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = (IsAuthenticated, )

    @action(
        detail=True,
        methods=('post',)
    )
    def follow_group(self, request, pk):
        group = self.get_object()
        serializer = GroupSubscriptionSerializer(
            data={'user': request.user.id, 'group': group.pk}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=HTTPStatus.CREATED)

    @action(
        detail=True,
        methods=('delete',)
    )
    def unfollow_group(self, request, pk):
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

    @action(
        detail=False,
        methods=('post',)
    )
    def create_group(self, request):
        serializer = GroupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(owner=request.user)
            return Response(serializer.data, status=HTTPStatus.CREATED)
        return Response(serializer.errors, status=HTTPStatus.BAD_REQUEST)

    @action(
        detail=True,
        methods=('delete',),
        permission_classes=(IsOwnerAdminOrReadOnly, )
    )
    def delete_group(self, request, pk):
        instance = self.get_object()
        if request.user == instance.owner:
            self.perform_destroy(instance)
            return Response(status=HTTPStatus.NO_CONTENT)
        else:
            return Response(
                {'detail': 'Вы не владелец группы.'},
                status=HTTPStatus.FORBIDDEN
            )

class HashtagViewSet(viewsets.ModelViewSet):
    queryset = Hashtag.objects.all()
    serializer_class = HashtagSerializer

    @action(detail=False, methods=['get'])
    def search_posts_by_hashtag(self, request):
        hashtag_name = request.query_params.get('hashtag', None)

        if not hashtag_name:
            return Response({"error": "Хэштег не указан"}, status=400)

        try:
            hashtag = Hashtag.objects.get(name=hashtag_name)
        except Hashtag.DoesNotExist:
            return Response({"error": "Хэштег не найден"}, status=404)

        posts = hashtag.posts.all()
        serializer = PostSerializer(posts, many=True)

        return Response(serializer.data)


class PostViewSet(viewsets.ModelViewSet):
    """Посты."""
    queryset = Post.objects.select_related('author', 'group').all()
    serializer_class = PostSerializer
    # permission_classes = (IsAuthorAdminOrReadOnly, )

    def perform_create(self, serializer):
        if self.request.method in ['PATCH', 'PUT', 'DELETE']:
            return [IsAuthorAdminOrReadOnly()]
        return [permissions.IsAuthenticatedOrReadOnly()]

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(detail=True, methods=('post', ))
    def create_comment(self, request, pk):
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

    @action(detail=True, methods=['POST'])
    def like(self, request, pk=None):
        post = self.get_object()
        like = request.user.likes.filter(post=post).all()
        if like:
            like.delete()
            return Response('Успешно удалено', 200)
        like = Like.objects.create(
            post=post,
            owner=request.user
        )
        return Response('успешно добавлено', 201)
    
    @action(detail=False, methods=['GET'])
    def recomend(self, request):
        rec_post = Post.objects.annotate(num_likes=Count('like_post')).order_by('-num_likes')
        serializer = PostSerializer(rec_post, many=True)
        return Response(serializer.data, status=200)       

class AsyncFeedViewSet(viewsets.ModelViewSet):
    serializer_class = FeedSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ('get',)

    async def async_get_queryset(self):
        user = self.request.user
        following_users = Follow.objects.filter(
            user=user).values_list('author', flat=True)
        queryset = Post.objects.filter(
            author__in=following_users).order_by('-pub_date')
        return queryset

    @async_to_sync
    async def get_queryset(self):
        return await self.async_get_queryset()

