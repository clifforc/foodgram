from django.contrib import admin
from django.db import models
from django.forms import CheckboxSelectMultiple

from .models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)


class RecipeIngredientInline(admin.TabularInline):
    model = RecipeIngredient
    extra = 0


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
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

    def favorite_count(self, obj):
        return Favorite.objects.filter(recipe=obj).count()

    def get_tags(self, obj):
        return ", ".join(
            obj.tags.values_list('name', flat=True).order_by('name'))

    favorite_count.short_descriptrion = "В избранном"
    get_tags.short_description = "Теги"


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        "name",
        "measurement_unit",
    )
    search_fields = [
        "name",
    ]


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    search_fields = [
        "name",
    ]


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ("user", "recipe")


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ("user", "recipe")
