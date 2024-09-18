from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

from foodgram import constants

User = get_user_model()

class SignUpSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('email', 'username', 'first_name', 'last_name', 'password')

        def validate_password(self, value):
            validate_password(value)
            return value

        def validate_username(self, value):
            if value == constants.NOT_ALLOWED_USERNAME:
                raise serializers.ValidationError(
                    {"username": f"Использовать имя {value} "
                                 "в качестве username запрещено."})
            elif User.objects.filter(username=value).exists():
                raise serializers.ValidationError(
                    {"username": "Пользователь "
                                 f"с именем {value} уже существует"})
            return value

        def validate_email(self, value):
            if User.objects.filter(email=value).exists():
                raise serializers.ValidationError(
                    {"email": f"Пользователь с адресом {value} уже существует"}
                )
            return value

        def create(self, validated_data):
            user = User.objects.create_user(
                email=validated_data['email'],
                username=validated_data['username'],
                first_name=validated_data['firts_name'],
                last_name=validated_data['last_name'],
                password=validated_data['password']
            )
            return user


class UserSerializer(serializers.ModelSerializer):
    # is_subscribed = serializers.BooleanField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            # 'is_subscribed',
            'avatar'
        )

    # def get_is_subscribed(self, obj):
    #     request = self.context.get('request')
    #     if request and request.user.is_authenticated:
    #         return obj.subscriber.filter(user=request.user).exists()
    #     return False


# class TokenSerializer(serializers.ModelSerializer):