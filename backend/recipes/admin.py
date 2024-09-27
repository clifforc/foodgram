from django.contrib import admin
from django.db import models
from django.forms import CheckboxSelectMultiple

from .models import Favorite, Ingredient, Recipe, RecipeIngredient, ShoppingCart, Tag


class RecipeIngredientInline(admin.TabularInline):
    """
    Интерфейс для модели RecipeIngredient.

    Позволяет редактировать ингредиенты рецепта непосредственно в форме рецепта.
    """

    model = RecipeIngredient
    extra = 0


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    """
    Настройки интерфейса администратора для модели Recipe.
    """

    list_display = (
        "name",
        "author",
        "favorite_count",
        "get_tags",
    )
    search_fields = [
        "author__username",
        "name",
    ]
    list_filter = [
        "tags",
    ]
    inlines = [RecipeIngredientInline]
    fieldsets = (
        (None, {"fields": ("name", "author", "tags")}),
        ("Описание", {"fields": ("text", "cooking_time", "image")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "name",
                    "author",
                    "tags",
                    "text",
                    "cooking_time",
                    "ingredients",
                    "image",
                ),
            },
        ),
    )
    formfield_overrides = {
        models.ManyToManyField: {"widget": CheckboxSelectMultiple},
    }

    def favorite_count(self, obj: Recipe) -> int:
        """
        Получить количество раз, когда рецепт был добавлен в избранное.

        Args:
            obj (Recipe): Экземпляр модели Recipe.
        Returns:
            int: Количество добавлений в избранное.
        """
        return Favorite.objects.filter(recipe=obj).count()

    def get_tags(self, obj: Recipe) -> str:
        """
        Получить теги рецепта в виде строки.

        Args:
            obj (Recipe): Экземпляр модели Recipe.
        Returns:
            str: Строка с перечислением тегов рецепта.
        """
        return ", ".join([tag.name for tag in obj.tags.all()])

    favorite_count.short_descriptrion = "В избранном"
    get_tags.short_description = "Теги"


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    """
    Настройки интерфейса администратора для модели Ingredient.
    """

    list_display = (
        "name",
        "measurement_unit",
    )
    search_fields = [
        "name",
    ]


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """
    Настройки интерфейса администратора для модели Tag.
    """

    list_display = ("name", "slug")
    search_fields = [
        "name",
    ]


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    """
    Настройки интерфейса администратора для модели Favorite.
    """

    list_display = ("user", "recipe")


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    """
    Настройки интерфейса администратора для модели ShoppingCart.
    """

    list_display = ("user", "recipe")
