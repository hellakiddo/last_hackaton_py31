import re

from django.core.exceptions import ValidationError


def validate_regex_username(value):
    """Проверка на отсутсвие запрещенных символов."""
    forbidden_symbols = "".join(set(re.sub(r"^[\w.@+-]+$", "", value)))
    if forbidden_symbols:
        raise ValidationError(
            f"Некорректный символ для никнейма: {forbidden_symbols}"
            f" Только буквы, цифры и @/./+/-/_"
        )
    return value