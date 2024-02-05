from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from . import constants
from .validators import validate_regex_username

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
    date_of_birth = models.DateField(
        "Дата рождения", null=True, blank=True
    )
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = [
        "first_name", "last_name", "username", 'date_of_birth'
    ]

    class Meta:
        ordering = ("username",)
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.username

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField('О себе', blank=True)
    icon = models.ImageField('Аватар', upload_to='media/', blank=True, null=True)

    class Meta:
        ordering = ("user",)
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"

    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()