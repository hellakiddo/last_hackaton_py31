from rest_framework.views import APIView
from rest_framework.response import Response
from django.db.models import Count

from posts.models import Post
from posts.serializers import PostSerializer


class RecomendationPost(APIView):
    def get(self, request):
        # Выбираем посты и считаем количество лайков для каждого поста
        rec_post = Post.objects.annotate(num_likes=Count('like_post')).order_by('-num_likes')
        serializer = PostSerializer(rec_post, many=True)
        return Response(serializer.data, status=200)
