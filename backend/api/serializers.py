from rest_framework import serializers
from djoser.serializers import UserCreateSerializer, UserSerializer, SetPasswordSerializer
from django.contrib.auth import get_user_model

from users.models import Subscription
from recipes.models import Tag, Ingredient

User = get_user_model()


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ('id','username','first_name','last_name','email', 'password')
        extra_kwargs = {'password': {'write_only': True}}


class CustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        model = User
        fields = ('id','username','first_name','last_name','email', 'is_subscribed', 'avatar')

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Subscription.objects.filter(user=request.user, author=obj).exists()
        return False


class CustomUserSetPasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')
