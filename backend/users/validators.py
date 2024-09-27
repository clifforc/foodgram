from django.core.exceptions import ValidationError

from foodgram import constants


def validate_username_not_me(value: str) -> None:
    """
    Проверяем что username не является запрещенным.

    Args:
        value (str): Имя пользователя для проверки.
    Raises:
        ValidationError: Если имя пользователя совпадает с запрещенным значением.
    """

    if value == constants.NOT_ALLOWED_USERNAME:
        raise ValidationError(
            f"Использовать имя '{value}' "
            "в качестве username запрещено."
        )
