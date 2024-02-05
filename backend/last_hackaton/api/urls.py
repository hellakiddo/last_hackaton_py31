from rest_framework.routers import DefaultRouter
from django.urls import path, include
from rest_framework import permissions
from drf_yasg.views import get_schema_view
from drf_yasg import openapi

from users.views import UserViewSet, ProfileViewSet
from posts.views import GroupViewSet, PostViewSet, FollowViewSet, AsyncFeedViewSet


app_name = "api"

router = DefaultRouter()

router.register(r"users", UserViewSet, basename="users")
router.register(r"groups", GroupViewSet, basename="groups")
router.register(r"posts", PostViewSet, basename="posts")
router.register(r"follows", FollowViewSet, basename="follows")
router.register(r'feeds', AsyncFeedViewSet, basename='feed')
router.register(r'profiles', ProfileViewSet, basename='profile')

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
    path("", include(router.urls)),
    path("auth/", include("djoser.urls.authtoken")),
    path('swagger/', schema_view.with_ui('swagger', cache_timeout=0),
         name='schema-swagger-ui'),
    path('redoc/', schema_view.with_ui('redoc', cache_timeout=0),
         name='schema-redoc'),
]
