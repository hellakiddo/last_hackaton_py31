from django.core.validators import RegexValidator

name_validator = RegexValidator(
    regex=r'^#[^\s]+$',
    message='Хэштэг должен начинаться с "#" и не содержать пробелов.',
)
