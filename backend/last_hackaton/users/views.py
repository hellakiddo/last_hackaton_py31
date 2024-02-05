from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from djoser.views import UserViewSet as DjoserUserViewSet

from .models import User, Profile
from .serializers import UserSerializer, ProfileSerializer
from posts.permissions import IsAuthorAdminOrReadOnly


class UserViewSet(DjoserUserViewSet):
    """Вьюсет для модели User"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)

class ProfileViewSet(viewsets.ModelViewSet):
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    permission_classes = (IsAuthenticated, )
    lookup_field = 'user__username'
    @action(
        detail=False, methods=('post', 'get', 'delete'),
        permission_classes=(IsAuthorAdminOrReadOnly,)
    )
    def my_profile(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

