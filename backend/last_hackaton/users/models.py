from django.contrib.auth.models import AbstractUser
from django.db import models

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
        validators=(validate_regex_username, ),
    )
    email = models.EmailField(
        "Email",
        max_length=constants.EMAIL_MAX_LENGHT,
        unique=True,
    )
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ("first_name", "last_name", "username")
    class Meta:
        ordering = ("username",)
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    def __str__(self):
        return self.username
