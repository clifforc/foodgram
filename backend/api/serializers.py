from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from django.db import transaction
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from api.fields import Base64ImageField
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


class CustomUserCreateSerializer(UserCreateSerializer):
    class Meta(UserCreateSerializer.Meta):
        model = User
        fields = ("id", "username", "first_name", "last_name", "email",
                  "password")
        extra_kwargs = {"password": {"write_only": True}}


class BaseCustomUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    def get_is_subscribed(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return Subscription.objects.filter(user=request.user,
                                               author=obj).exists()
        return False


class CustomUserSerializer(BaseCustomUserSerializer):
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

    def update(self, instance, validated_data):
        if 'avatar' in validated_data and instance.avatar:
            instance.avatar.delete()
        return super().update(instance, validated_data)


class SubscriptionSerializer(BaseCustomUserSerializer):
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
        queryset = obj.recipes.all()
        limit = self.context.get("recipes_limit")
        if limit:
            queryset = queryset[: int(limit)]
        return RecipeMiniSerializer(queryset, many=True).data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class CustomUserSetPasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True,
                                         validators=[validate_password])

    def validate(self, data):
        user = self.context['request'].user
        if not user.check_password(data.get('current_password')):
            raise serializers.ValidationError(
                "Пароль не соответсвует текущему.")
        return data


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ("id", "name", "slug")


class IngredientsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ("id", "name", "measurement_unit")


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source="ingredient.id")
    name = serializers.ReadOnlyField(source="ingredient.name")
    measurement_unit = serializers.ReadOnlyField(
        source="ingredient.measurement_unit")

    class Meta:
        model = RecipeIngredient
        fields = ("id", "name", "measurement_unit", "amount")


class RecipeMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ("id", "name", "image", "cooking_time")


class RecipeSerializer(serializers.ModelSerializer):
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
        if not value:
            raise serializers.ValidationError("Нужно добавить тег.")
        tags = set()
        for tag in value:
            if tag in tags:
                raise serializers.ValidationError(
                    "Тэги не должны повторяться.")
            tags.add(tag)
        return value

    def recipe_ingredients_create(self, recipe, ingredients_data):
        for ingredient_data in ingredients_data:
            ingredient_id = ingredient_data["ingredient"]["id"]
            RecipeIngredient.objects.create(
                recipe=recipe, ingredient_id=ingredient_id,
                amount=ingredient_data["amount"]
            )

    @transaction.atomic
    def create(self, validated_data):
        ingredients_data = validated_data.pop("recipeingredient_set")
        tags_data = validated_data.pop("tags")
        image_data = validated_data.pop("image")

        recipe = Recipe.objects.create(**validated_data)
        recipe.image.save(image_data.name, image_data, save=True)

        self.recipe_ingredients_create(recipe, ingredients_data)

        recipe.tags.set(tags_data)
        return recipe

    def update(self, instance, validated_data):
        tags_data = validated_data.pop("tags", None)
        ingredients_data = validated_data.pop("recipeingredient_set", None)

        self.validate_ingredients(ingredients_data)
        self.validate_tags(tags_data)

        instance = super().update(instance, validated_data)

        if tags_data is not None:
            instance.tags.set(tags_data)

        if ingredients_data is not None:
            instance.recipeingredient_set.all().delete()
            self.recipe_ingredients_create(instance, ingredients_data)

        return instance

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        representation["tags"] = TagSerializer(instance.tags.all(),
                                               many=True).data
        return representation

    def get_is_favorited(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return Favorite.objects.filter(user=request.user,
                                           recipe=obj).exists()
        return False

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get("request")
        if request and request.user.is_authenticated:
            return ShoppingCart.objects.filter(user=request.user,
                                               recipe=obj).exists()
        return False
