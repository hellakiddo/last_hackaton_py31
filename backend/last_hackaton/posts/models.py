from django.db import models
from slugify import slugify

from users.models import User, Hashtag

from posts.validators import name_validator


class Group(models.Model):
    """ ORM модель групп """
    title = models.CharField('Название группы', max_length=200,
                             help_text='Дайте название группе')
    slug = models.SlugField('URL адрес', unique=True, blank=True, null=True)
    description = models.TextField('Описание группы',
                                   max_length=10000,
                                   default='some string',
                                   help_text='Описание для группы')
    owner = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='owned_groups',
        verbose_name='Владелец'
    )
    image = models.ImageField(
        'Изображение группы', upload_to='media/',
        null=True, blank=True
    )

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'
        ordering = ('-title',)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(str(self.title))
        super().save(*args, **kwargs)

class GroupSubscription(models.Model):
    """ORM модель подписок на группы."""
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='group_subscriptions'
    )
    group = models.ForeignKey(
        Group, on_delete=models.CASCADE,
        related_name='group_subscriptions'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'group'], name='unique_group_subscription'
            )
        ]
        verbose_name = "Подписка на группу"
        verbose_name_plural = "Подписки на группу"



class Post(models.Model):
    """ ORM модель постов """
    text = models.TextField(
        'Текст поста', max_length=15000, help_text='Напишите что-нибудь...'
    )
    pub_date = models.DateTimeField(
        'Дата публикации', auto_now_add=True, db_index=True
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='posts', verbose_name='Автор'
    )
    group = models.ForeignKey(
        Group, blank=True, null=True,
        on_delete=models.SET_NULL,
        related_name='posts',
        verbose_name='Группа', help_text='Группа поста'
    )
    image = models.ImageField(
        'Картинка', upload_to='posts/',
        blank=True, null=True
    )
    video = models.FileField(
        'Видео', upload_to='media/',
        blank=True, null=True
    )
    hashtags = models.ManyToManyField(
        Hashtag, related_name='posts',
        blank=True,
        verbose_name='Хэштэги'
    )
    parent_post = models.ForeignKey(
        'self', on_delete=models.CASCADE,
        null=True, blank=True, related_name='replies'
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name_plural = 'Посты'

    def __str__(self):
        return f"{self.author.username} - {self.text[:50]}"

    def save(self, *args, **kwargs):
        if self.group and self.author != self.group.owner:
            raise ValueError("Только автор группы может добавить пост.")
        super().save(*args, **kwargs)
        words = self.text.split()  # Изменено на self.text
        hashtags = [word[1:] for word in words if word.startswith('#')]
        for hashtag_text in hashtags:
            hashtag, created = Hashtag.objects.get_or_create(name=hashtag_text)
            if hashtag:
                self.hashtags.add(hashtag)  # Использован метод add для добавления объекта хэштега

    
    @staticmethod
    def search_by_hashtag(hashtag_name):
        """Метод для поиска постов по хештегу"""
        return Post.objects.filter(hashtags__name=hashtag_name)



class Comment(models.Model):
    """ ORM модель комментариев """
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE, related_name='comments'
    )
    author = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='comments', verbose_name='Автор')
    text = models.TextField(
        'Текст комментария', max_length=10000,
        help_text='Напишите что-нибудь...')
    pub_date = models.DateTimeField(
        'Дата публикации', auto_now_add=True)
    parent_comment = models.ForeignKey(
        'self', on_delete=models.CASCADE,
        null=True, blank=True, related_name='replies')

    class Meta:
        ordering = ('-pub_date',)
        verbose_name_plural = 'Комментарии'

    def __str__(self):
        return f'Комментарий от {self.author}'



class Feed(models.Model):
    """ORM модель ленты."""
    user = models.ForeignKey(
        User, on_delete=models.CASCADE,
        related_name='feed',
        verbose_name='Пользователь'
    )
    post = models.ForeignKey(
        Post, on_delete=models.CASCADE,
        related_name='feed_posts',
        verbose_name='Пост', null=True)
    group_post = models.ForeignKey(
        Post, on_delete=models.CASCADE,
        related_name='group_feed_posts',
        verbose_name='Пост группы', null=True)

    class Meta:
        verbose_name = 'Лента'
        verbose_name_plural = 'Ленты'