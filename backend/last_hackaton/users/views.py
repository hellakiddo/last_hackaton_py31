from http import HTTPStatus

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from djoser.views import UserViewSet as DjoserUserViewSet

from .models import User, Profile, Follow
from .serializers import UserSerializer, ProfileSerializer, FollowSerializer
from posts.permissions import IsAuthorAdminOrReadOnly

from posts.permissions import IsOwnerAdminOrReadOnly


class UserViewSet(DjoserUserViewSet):
    """Вьюсет для модели User"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)

class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = (IsOwnerAdminOrReadOnly, )
    @action(
        detail=False, methods=('post', 'get', 'delete'),
        permission_classes=(IsAuthorAdminOrReadOnly,)
    )
    def my_profile(self, request):
        serializer = ProfileSerializer(
            request.user.profile, context={'request': request}
        )
        return Response(serializer.data)

    @action(
        methods=("post",),
        detail=True,
        permission_classes=(IsAuthenticated,),
    )
    def follow(self, request, pk):
        """Метод для создания подписки."""
        data = {"user": request.user.id, "author": pk}
        serializer = FollowSerializer(
            data=data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=HTTPStatus.CREATED)

    @follow.mapping.delete
    def delete_follow(self, request, pk):
        subscription = Follow.objects.filter(
            user=request.user, author_id=pk
        )
        if subscription.exists():
            subscription.delete()
            return Response(status=HTTPStatus.NO_CONTENT)
        return Response(status=HTTPStatus.BAD_REQUEST)
