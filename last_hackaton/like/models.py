from django.db import models

from users.models import User
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


    class Meta:
        unique_together = ['owner', 'post']