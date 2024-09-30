import shortuuid
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone

from foodgram import constants

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(
        max_length=constants.INGREDIENT_NAME_MAX_LENGTH,
        verbose_name="Наименование"
    )
    measurement_unit = models.CharField(
        max_length=constants.MEASUREMENT_MAX_LENGTH,
        verbose_name="Единица измерения"
    )

    class Meta:
        verbose_name = "ингредиент"
        verbose_name_plural = "Ингредиенты"

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(
        max_length=constants.TAG_MAX_LENGTH, unique=True,
        verbose_name="Название"
    )
    slug = models.SlugField(
        max_length=constants.TAG_MAX_LENGTH, unique=True,
        verbose_name="Слаг"
    )

    class Meta:
        verbose_name = "тэг"
        verbose_name_plural = "Тэги"

    def __str__(self):
        return self.name


class Recipe(models.Model):
    tags = models.ManyToManyField(
        Tag,
        related_name="recipes",
        verbose_name="Тэги"
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="recipes",
        verbose_name="Автор"
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through="RecipeIngredient",
        verbose_name="Ингредиенты"
    )
    name = models.CharField(
        max_length=constants.NAME_MAX_LENGTH,
        verbose_name="Название"
    )
    image = models.ImageField(
        upload_to="recipes/",
        verbose_name="Изображение"
    )
    text = models.TextField(verbose_name="Описание")
    cooking_time = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Время приготовления"
    )
    short_link = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        unique=True,
        verbose_name="Короткая ссылка",
    )
    created_at = models.DateTimeField(default=timezone.now)

    def get_or_create_short_link(self):
        if not self.short_link:
            self.short_link = shortuuid.uuid()[:8]
            self.save(update_fields=["short_link"])
        return self.short_link

    class Meta:
        verbose_name = "рецепт"
        verbose_name_plural = "Рецепты"

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name="Рецепт"
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name="Ингредиент"
    )
    amount = models.PositiveIntegerField(
        validators=[MinValueValidator(1)],
        verbose_name="Количество"
    )

    class Meta:
        constraints =[
            models.UniqueConstraint(name="unique_recipe_ingredient",
                                    fields=["recipe", "ingredient"])
        ]

    def __str__(self):
        return (
            f"{self.ingredient.name} - "
            f"{self.amount} "
            f"{self.ingredient.measurement_unit}"
        )


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="favorites",
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="favorited_by",
        verbose_name="Рецепт",
    )

    class Meta:
        verbose_name = "избранное"
        verbose_name_plural = "Избранное"
        constraints = [
            models.UniqueConstraint(name="unique_favorite",
                                    fields=["user", "recipe"])
        ]
    def __str__(self):
        return f"{self.recipe.name} в избранном у {self.user.username}"


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="shoping_cart",
        verbose_name="Пользователь",
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name="in_shopping_cart",
        verbose_name="Рецепт",
    )

    class Meta:
        verbose_name = "Список покупок"
        verbose_name_plural = "Список покупок"
        constraints = [
            models.UniqueConstraint(name='unique_shopping_cart',
                                    fields=["user", "recipe"])
        ]

    def __str__(self):
        return f"{self.recipe.name} в корзине у {self.user.username}"
