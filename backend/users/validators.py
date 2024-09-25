from django.core.exceptions import ValidationError

from foodgram import constants


def validate_username_not_me(value: str) -> None:
    """
    Проверяем что username не является запрещенным.

    :param value: Имя пользователя.
    :raise ValidationError: Если имя пользователя использовать запрещено.
    """

    if value == constants.NOT_ALLOWED_USERNAME:
        raise ValidationError(
            f"Использовать имя '{value}' "
            "в качестве username запрещено."
        )
