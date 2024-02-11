from rest_framework.routers import DefaultRouter
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework_simplejwt.views import (
    TokenObtainPairView, TokenRefreshView
)

from posts.views import GroupViewSet, PostViewSet, AsyncFeedViewSet, HashtagViewSet

from users.views import (
    ProfileViewSet,
    RegistrationView,
    ActivationView,
    LogoutView,
    CustomResetPasswordView,
    CustomPasswordConfirmView,
)

app_name = "api"

router = DefaultRouter()

router.register(r"groups", GroupViewSet, basename="groups")
router.register(r"posts", PostViewSet, basename="posts")
router.register(r'feeds', AsyncFeedViewSet, basename='feed')
router.register(r'profiles', ProfileViewSet, basename='profile')
router.register(r'hashtags', HashtagViewSet, basename='hashtags')

schema_view = get_schema_view(
    openapi.Info(
        title="last_hackaton API",
        default_version='v1',
        description="last_hackaton API",
        terms_of_service="https://www.yourapp.com/terms/",
        contact=openapi.Contact(email="contact@yourapp.com"),
        license=openapi.License(name="МЕНТОРЫ ChocoPy31 КРАСАВЧИКИ"),
    ),
    public=True,
    permission_classes=[permissions.AllowAny],
)

urlpatterns = [
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0),
         name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0),
         name='schema-redoc'),
    path('register/', RegistrationView.as_view()),
    path('activate/', ActivationView.as_view()),
    path('login/', TokenObtainPairView.as_view()),
    path('refresh/', TokenRefreshView.as_view()),
    path('logout/', LogoutView.as_view()),
    path('reset_password/', CustomResetPasswordView.as_view()),
    path('password_confirm/<uidb64>/', CustomPasswordConfirmView.as_view()),
    path('', include(router.urls)),
]
