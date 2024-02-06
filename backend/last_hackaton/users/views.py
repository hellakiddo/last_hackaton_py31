from http import HTTPStatus

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from djoser.views import UserViewSet as DjoserUserViewSet

from .models import User, Profile, Follow
from .serializers import UserSerializer, ProfileSerializer, FollowSerializer
from .permissions import IsOwnerAdminOrReadOnly


class UserViewSet(DjoserUserViewSet):
    """Вьюсет для модели User"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)

class ProfileViewSet(viewsets.ModelViewSet):
    """Профиль пользователей."""
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = (IsOwnerAdminOrReadOnly, )
    @action(
        detail=False, methods=('get',),
        permission_classes=(IsOwnerAdminOrReadOnly,)
    )
    def my_profile(self, request):
        """Профиль текущего пользователя."""
        serializer = ProfileSerializer(
            request.user.profile, context={'request': request}
        )
        return Response(serializer.data)

    @action(
        detail=True, methods=('put', 'patch'),
        permission_classes=(IsOwnerAdminOrReadOnly,)
    )
    def update_profile(self, request, pk):
        """Обновить профиль текущего пользователя."""
        profile = self.get_object()
        serializer = ProfileSerializer(
            profile, data=request.data, context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    @action(
        detail=True, methods=('delete',),
        permission_classes=(IsOwnerAdminOrReadOnly,)
    )
    def delete_profile(self, request, pk):
        profile = self.get_object()
        user = profile.user
        profile.delete()
        user.delete()
        return Response(
            {'detail': 'Профиль удален.'}, status=HTTPStatus.NO_CONTENT
        )

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
