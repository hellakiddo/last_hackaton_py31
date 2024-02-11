from typing import Iterable
from django.db import models

from users.models import User, Profile, Hashtag
from posts.models import Post

class Like(models.Model):
    owner =  models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='likes'
    )
    post = models.ForeignKey(
        Post,
        related_name='likes',
        on_delete=models.CASCADE
    )


    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Получаем пользователя, который поставил лайк
        user = self.owner
        if user:
            first_hashtag_name = self.post.hashtags.first()
            if first_hashtag_name:
                # Получаем объект Hashtag по имени хэштега
                first_hashtag = Hashtag.objects.get(name=first_hashtag_name)
                # Получаем профиль пользователя
                try:
                    profile = User.objects.get(username=user)
                except Profile.DoesNotExist:
                    pass
                else:
                    # Проверяем, был ли уже добавлен этот хэштег в предпочтенный контент профиля
                    existing_hashtag = profile.preferred_content.filter(name=first_hashtag_name).exists()
                    if not existing_hashtag:
                        profile.preferred_content.add(first_hashtag)
    class Meta:
        unique_together = ['owner', 'post']


class Favorite(models.Model):
    post = models.ForeignKey(
        Post,
        related_name='favorites',
        on_delete=models.CASCADE
    )
    owner = models.ForeignKey(
        User,
        related_name='favorites',
        on_delete=models.CASCADE
    )