import shortuuid
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models
from django.utils import timezone
from foodgram import constants

User = get_user_model()


class Ingredient(models.Model):
    """
    Модель для представления ингредиентов.

    Attributes:
        name (CharField): Наименование ингредиента.
        measurement_unit (CharField): Единица измерения.
    """

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
    """
    Модель для представления тэгов.

    Attributes:
        name (CharField): Наименование тега.
        slug (SlugField): Слаг тега.
    """

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
    """
    Модель для представления рецептов.

    Эта модель хранит информацию о кулинарных рецептах, включая их ингредиенты,
    время приготовления, автора и связанные теги.

    Attributes:
        tags (ManyToManyField): Связь многие-ко-многим с моделью Tag.
        author (ForeignKey): Ссылка на пользователя, создавшего рецепт.
        ingredients (ManyToManyField): : Связь многие-ко-многим с моделью
            Ingredient через промежуточную модель RecipeIngredient.
        name (CharField): Название рецепта.
        image (ImageField): Изображение рецепта.
        text (TextField): Текстовое описание рецепта.
        cooking_time (PositiveIntegerField): Время приготовления.
        short_link (CharField): Уникальная короткая ссылка для доступа
            к рецепту.
        created_at (DateTimeField): Дата и время создания рецепта.
    """

    tags = models.ManyToManyField(Tag, related_name="recipes",
                                  verbose_name="Тэги")
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="recipes",
        verbose_name="Автор"
    )
    ingredients = models.ManyToManyField(
        Ingredient, through="RecipeIngredient", verbose_name="Ингредиенты"
    )
    name = models.CharField(
        max_length=constants.NAME_MAX_LENGTH, verbose_name="Название"
    )
    image = models.ImageField(upload_to="recipes/", verbose_name="Изображение")
    text = models.TextField(verbose_name="Описание")
    cooking_time = models.PositiveIntegerField(
        validators=[MinValueValidator(1)], verbose_name="Время приготовления"
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
        """
        Возвращает существующую короткую ссылку или создает новую.

        Returns:
            str: Короткая ссылка для рецепта.
        """

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
    """
    Модель для представления связи между моделями рецептов и ингредиентов.

    Эта модель позволяет указать количество ингредиента, необходимого
    для приготовления рецепта.

    Attributes:
        recipe (ForeignKey): Связь с моделью Recipe.
        ingredient (ForeignKey): Связь с моделью Ingredient.
        amount (PositiveIntegerField): Количество ингредиента, необходимое
            для рецепта.
    """

    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE,
                               verbose_name="Рецепт")
    ingredient = models.ForeignKey(
        Ingredient, on_delete=models.CASCADE, verbose_name="Ингредиент"
    )
    amount = models.PositiveIntegerField(
        validators=[MinValueValidator(1)], verbose_name="Количество"
    )

    class Meta:
        unique_together = ["recipe", "ingredient"]

    def __str__(self):
        return (
            f"{self.ingredient.name} - "
            f"{self.amount} "
            f"{self.ingredient.measurement_unit}"
        )


class Favorite(models.Model):
    """
    Модель для представления избранных рецептов пользователя.

    Эта модель позволяет пользователям отмечать рецепты как избранные,
    создавая связь между пользователем и рецептом.

    Attributes:
        user (ForeignKey): Связь с моделью User.
        recipe (ForeignKey): Связь с моделью Recipe.
    """

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
        unique_together = ["user", "recipe"]

    def __str__(self):
        return f"{self.recipe.name} в избранном у {self.user.username}"


class ShoppingCart(models.Model):
    """
    Модель для представления списка покупок пользователя.

    Эта модель позволяет пользователям добавлять рецепты в список покупок,
    чтобы потом использовать для составления списка необходимых ингредиентов.

    Attributes:
        user (ForeignKey): Связь с моделью User.
        recipe (ForeignKey): Связь с моделью Recipe.
    """

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
        unique_together = ["user", "recipe"]

    def __str__(self):
        return f"{self.recipe.name} в корзине у {self.user.username}"
