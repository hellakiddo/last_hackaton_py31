from drf_yasg.utils import swagger_auto_schema
from http import HTTPStatus

from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import permissions
from rest_framework_simplejwt.views import (
    TokenObtainPairView, TokenRefreshView
)

from .models import User, Profile, Follow
from .serializers import (
    UserSerializer, ProfileSerializer, FollowSerializer, LogOutSerialzer
)
from .permissions import IsOwnerAdminOrReadOnly
from .tasks import send_confirm_email_task, send_password_reset_task
from posts.models import Post
from posts.serializers import PostSerializer, FavoriteSerializer


#  =================== Регистрация =====================

class RegistrationView(APIView):
    serializer_class = UserSerializer

    @swagger_auto_schema(
        request_body=serializer_class,
        responses={201: 'Created', 400: 'Bad Request'}
    )
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        if user:
            try:
                send_confirm_email_task.delay(
                    user.email, user.activation_code
                )
            except:
                return Response(
                    {
                        'message': 'Ошибка отправки на почту.',
                        'data': serializer.data
                    }, status=HTTPStatus.CREATED
                )
            return Response(serializer.data, status=HTTPStatus.CREATED)

#  =================== Активация =====================
class ActivationView(APIView):
    def get(self, request):
        code = request.query_params.get('u')
        user = get_object_or_404(User, activation_code=code)
        user.is_active = True
        user.activation_code = ''
        user.save()
        return Response('Активирован', status=HTTPStatus.OK)

#  =================== Логаут =====================
class LogoutView(APIView):
    serializer_class = LogOutSerialzer
    permission_classes = (permissions.IsAuthenticated, )

    def post(self, request):
        refresh_token = request.data.get('refresh')
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response('Успешно разлогинилсь', status=HTTPStatus.OK)


class CustomResetPasswordView(APIView):
    def post(self, request):
        email = request.data.get('email')
        user = User.objects.get(email=email)
        user_id = user.id
        if not user:
            return Response(
                {'ValidationError': 'Нет такого пользователя'},
                status=HTTPStatus.BAD_REQUEST
            )

        send_password_reset_task.delay(email=email, user_id=user_id)
        return Response(
            'Сообщения отправлено на почту.', status=HTTPStatus.OK
        )


class CustomPasswordConfirmView(APIView):
    def post(self, request, *args, **kwargs):
        new_password = request.data.get('new_password')
        password_confirm = request.data.get('password_confirm')
        user_id = self.kwargs.get('uidb64')
        user = User.objects.get(id=user_id)
        if new_password != password_confirm:
            return Response(
                'Пароли не совпадают', status=HTTPStatus.BAD_REQUEST
            )
        user.set_password(new_password)
        user.save()
        return Response('Ваш пароль изменен!', status=HTTPStatus.CREATED)

#  =================== Токены =====================
class LoginView(TokenObtainPairView):
    permission_classes = (AllowAny, )


class RefreshView(TokenRefreshView):
    permission_classes = (AllowAny, )

#  =================== Профиль =====================
class ProfileViewSet(viewsets.ModelViewSet):
    """Профиль пользователей."""
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = (IsOwnerAdminOrReadOnly, )
    @action(
        detail=False, methods=('get',),
        permission_classes=(IsOwnerAdminOrReadOnly, IsAuthenticated)
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


# ===============Recomendation===================
class RecomendationAPIView(APIView):
    """Рекомендации по предпочитаемым контентам пользователя"""
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        user = request.user
        preferred_content = user.preferred_content.all()  # Получаем предпочтения пользователя
        recommended_posts = Post.objects.none()
        
        for hashtag in preferred_content:
            # Формируем запрос для поиска постов, у которых хотя бы один из хэштегов соответствует предпочтению пользователя
            posts_with_hashtag = Post.objects.filter(hashtags=hashtag)
            recommended_posts = recommended_posts | posts_with_hashtag
        
        recommended_posts = recommended_posts.distinct()

        serializer = PostSerializer(recommended_posts, many=True)

        return Response(serializer.data)


# ================Favorites====================

class FavoriteAPIView(APIView):
    """ Получение избранных постов """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        favorite = request.user.favorites.all()
        serializer = FavoriteSerializer(favorite, many=True)
        if serializer.data:
            return Response(serializer.data, 200)
        return Response('Нет избранных постов',200)
    