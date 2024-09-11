from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models

from validators import validate_username_not_me
from ..foodgram import constants

class User(AbstractUser):
    email = models.EmailField(
        max_length=constants.EMAIL_MAX_LENGTH,
        unique=True
    )
    username = models.CharField(
        max_length=constants.USERNAME_MAX_LENGTH,
        unique=True,
        validators=[UnicodeUsernameValidator(), validate_username_not_me],
        verbose_name='Имя пользователя'
    )
    avatar = models.ImageField(upload_to='users/', null=True, blank='True')