from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from django.db import models

from foodgram import constants

User = get_user_model()


class Ingredient(models.Model):
    name = models.CharField(max_length=constants.INGREDIENT_NAME_MAX_LENGTH)
    measurement_unit = models.CharField(
        max_length=constants.MEASUREMENT_MAX_LENGTH)

    def __str__(self):
        return f"{self.name}, {self.measurement_unit}"


class Tag(models.Model):
    name = models.CharField(max_length=constants.TAG_MAX_LENGTH)
    slug = models.SlugField(max_length=constants.TAG_MAX_LENGTH)

    def __str__(self):
        return self.name


class Recipe(models.Model):
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    name = models.CharField(max_length=constants.NAME_MAX_LENGTH)
    image = models.ImageField(upload_to='recipes/')
    text = models.TextField()
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient'
    )
    tags = models.ManyToManyField(Tag)
    cooking_time = models.PositiveIntegerField(
        validators=[MinValueValidator(1)]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient, on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(validators=[MinValueValidator(1)])

    class Meta:
        unique_together = ['recipe', 'ingredient']


class Favorite(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favorites')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='favorited_by')

    class Meta:
        unique_together = ['user', 'recipe']


class ShoppingCart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='shoping_cart')
    recipe = models.ForeignKey(Recipe, on_delete=models.CASCADE, related_name='in_shopping_cart')

    class Meta:
        unique_together = ['user', 'recipe']


class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscriptions')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='subscribers')

    class Meta:
        unique_together = ['user', 'author']
