from django.core.exceptions import ValidationError

from foodgram import constants


def validate_username_not_me(value):
    if value == constants.NOT_ALLOWED_USERNAME:
        raise ValidationError(
            f"Использовать имя '{value}' " "в качестве username запрещено."
        )
