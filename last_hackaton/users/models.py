from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import UniqueConstraint, CheckConstraint
from django.db.models.signals import post_save
from django.dispatch import receiver

from . import constants
from .validators import validate_regex_username


class UserManager(BaseUserManager):
    """Модель Менеджера."""
    use_in_migrations = True

    def _create_user(self, email, password, **kwargs):
        if not email:
            return ValueError('почта должна обяз передаваться')
        email = self.normalize_email(email=email)
        user = self.model(email=email, **kwargs)
        user.create_activation_code()
        user.set_password(password)
        user.save()
        return user

    def create_user(self, email, password, **kwargs):
        kwargs.setdefault('is_staff', False)
        kwargs.setdefault('is_superuser', False)
        return self._create_user(email, password, **kwargs)

    def create_superuser(self, email, password, **kwargs):
        kwargs.setdefault('is_staff', True)
        kwargs.setdefault('is_superuser', True)
        kwargs.setdefault('is_active', True)
        return self._create_user(email, password, **kwargs)


class User(AbstractUser):
    """Модель пользователя."""

    first_name = models.CharField(
        max_length=constants.FIRST_AND_LAST_USERNAME_MAX_LENGHT,
        verbose_name="Имя",
    )
    last_name = models.CharField(
        max_length=constants.FIRST_AND_LAST_USERNAME_MAX_LENGHT,
        verbose_name="Фамилия",
    )
    username = models.CharField(
        "Никнейм",
        max_length=constants.USERNAME_AND_PASSWORD_MAX_LENGHT,
        unique=True,
        validators=[validate_regex_username],
    )
    email = models.EmailField(
        "Email",
        max_length=constants.EMAIL_MAX_LENGHT,
        unique=True,
    )
    password = models.CharField(
        max_length=100
    )
    date_of_birth = models.DateField(
        "Дата рождения", null=True, blank=True
    )
    activation_code = models.CharField(
        max_length=255, blank=True
    )
    is_active = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [
        "first_name", "last_name", "username", 'date_of_birth'
    ]

    def create_activation_code(self):
        import uuid
        code = str(uuid.uuid4())
        self.activation_code = code

    class Meta:
        ordering = ("username",)
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.username

class Profile(models.Model):
    """Модель Профиля."""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField('О себе', blank=True)
    icon = models.ImageField('Аватар', upload_to='media/', blank=True, null=True)

    class Meta:
        ordering = ("user",)
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"

    def __str__(self):
        return self.user.username


class Follow(models.Model):
    """Модель Подпсики на пользователя."""
    user = models.ForeignKey(
        User,
        related_name='follower',
        on_delete=models.CASCADE,
        null=True
    )
    author = models.ForeignKey(
        User,
        related_name='following',
        on_delete=models.CASCADE,
        null=True
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        UniqueConstraint(fields=['author', 'user'], name='unique_subscription')
        CheckConstraint(name='prevent_self_follow', check=~models.Q(user=models.F('author')))

    def __str__(self):
        return '{} подписан на {}'.format(self.user, self.author)


# При создание User - создает Profile для него
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()