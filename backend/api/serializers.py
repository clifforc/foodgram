import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.db import transaction
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)
from users.models import Subscription

User = get_user_model()


class Base64ImageField(serializers.ImageField):
    """
    Поле для обработки изображений в формате base64.
    """

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith("data:image"):
            format, imgstr = data.split(";base64,")
            ext = format.split("/")[-1]
            data = ContentFile(base64.b64decode(imgstr), name="temp." + ext)
        return super().to_internal_value(data)


class CustomUserCreateSerializer(UserCreateSerializer):
    """
    Сериализатор для создания пользователя.
    """

    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ("id", "username", "first_name", "last_name", "email",
                  "password")
        extra_kwargs = {"password": {"write_only": True}}


class BaseCustomUserSerializer(UserSerializer):
    """
    Базовый сериализатор пользователя с дополнительным полем is_subscribed.
    """

    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        """
        Проверяет, подписан ли текущий пользователь на данного автора.
        """

        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return Subscription.objects.filter(user=request.user,
                                               author=obj).exists()
        return False


class CustomUserSerializer(BaseCustomUserSerializer):
    """
    Расширенный сериализатор пользователя с полем аватара.
    """

    avatar = Base64ImageField()

    class Meta(UserSerializer.Meta):
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "is_subscribed",
            "avatar",
        )


class SubscriptionSerializer(BaseCustomUserSerializer):
    """
    Сериализатор для отображения подписок пользователя.
    """

    recipes_count = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()

    class Meta(UserSerializer.Meta):
        model = User
        fields = (
            "id",
            "username",
            "first_name",
            "last_name",
            "email",
            "is_subscribed",
            "avatar",
            "recipes_count",
            "recipes",
        )

    def get_recipes(self, obj):
        """
        Возвращает список рецептов автора с учетом лимита.
        """

        queryset = obj.recipes.all()
        limit = self.context.get("recipes_limit")
        print(queryset)
        if limit:
            queryset = queryset[: int(limit)]
        return RecipeMiniSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        """
        Возвращает количество рецептов автора.
        """

        return obj.recipes.count()


class CustomUserSetPasswordSerializer(serializers.Serializer):
    """
    Сериализатор для смены пароля пользователя.
    """

    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)


class TagSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели тегов.
    """

    class Meta:
        model = Tag
        fields = ("id", "name", "slug")


class IngredientsSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели ингредиентов.
    """

    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """
    Сериализатор для связи рецепта и ингредиента.
    """

    id = serializers.IntegerField(source="ingredient.id")
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit")

    class Meta:
        model = RecipeIngredient
        fields = ("id", "name", "measurement_unit", "amount")


class RecipeMiniSerializer(serializers.ModelSerializer):
    """
    Сериализатор для краткого представления рецепта.
    """

    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class RecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор для полного представления рецепта.
    """

    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all(), required=True
    )
    author = CustomUserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        many=True, required=True, source="recipeingredient_set"
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            "id",
            "tags",
            "author",
            "ingredients",
            "is_favorited",
            "is_in_shopping_cart",
            "name",
            "image",
            "text",
            "cooking_time",
        )

    def validate_ingredients(self, value):
        """
        Проверяет корректность данных об ингредиентах.
        """

        if not value:
            raise serializers.ValidationError("Нужно добавить ингредиенты.")
        ingredient_ids = set()
        for ingredient in value:
            ingredient_id = ingredient["ingredient"]["id"]
            if ingredient_id in ingredient_ids:
                raise serializers.ValidationError(
                    "Ингредиенты не должны повторяться.")
            ingredient_ids.add(ingredient_id)
            if not Ingredient.objects.filter(id=ingredient_id).exists():
                raise serializers.ValidationError("Ингредиент не существует.")
        return value

    def validate_tags(self, value):
        """
        Проверяет корректность данных о тегах.
        """

        if not value:
            raise serializers.ValidationError("Нужно добавить тег.")
        tags = set()
        for tag in value:
            if tag in tags:
                raise serializers.ValidationError(
                    "Тэги не должны повторяться.")
            tags.add(tag)
        return value

    @transaction.atomic
    def create(self, validated_data):
        """
        Создает новый рецепт.
        """

        ingredients_data = validated_data.pop("recipeingredient_set")
        tags_data = validated_data.pop("tags")
        image_data = validated_data.pop("image")

        recipe = Recipe.objects.create(**validated_data)

        recipe.image.save(image_data.name, image_data, save=True)

        for ingredient_data in ingredients_data:
            ingredient_id: int = ingredient_data["ingredient"]["id"]
            ingredient = Ingredient.objects.get(id=ingredient_id)
            RecipeIngredient.objects.create(
                recipe=recipe, ingredient=ingredient,
                amount=ingredient_data["amount"]
            )

        recipe.tags.set(tags_data)
        return recipe

    def update(self, instance, validated_data):
        """
        Обновляет существующий рецепт.
        """

        tags_data = validated_data.pop("tags", None)
        ingredients_data = validated_data.pop("recipeingredient_set", None)

        self.validate_ingredients(ingredients_data)
        self.validate_tags(tags_data)

        instance = super().update(instance, validated_data)

        if tags_data is not None:
            instance.tags.set(tags_data)

        if ingredients_data is not None:
            instance.recipeingredient_set.all().delete()
            for ingredient_data in ingredients_data:
                ingredient_id: int = ingredient_data["ingredient"]["id"]
                ingredient = Ingredient.objects.get(id=ingredient_id)
                RecipeIngredient.objects.create(
                    recipe=instance,
                    ingredient=ingredient,
                    amount=ingredient_data["amount"],
                )

        return instance

    def to_representation(self, instance):
        """
        Преобразует объект рецепта в словарь для сериализации.
        """

        representation = super().to_representation(instance)
        representation["tags"] = TagSerializer(instance.tags.all(),
                                               many=True).data
        return representation

    def get_is_favorited(self, obj):
        """
        Проверяет, добавлен ли рецепт в избранное пользователем.
        """

        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return Favorite.objects.filter(user=request.user,
                                           recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        """
        Проверяет, добавлен ли рецепт в список покупок пользователем.
        """

        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return ShoppingCart.objects.filter(user=request.user,
                                               recipe=obj).exists()
        return False
