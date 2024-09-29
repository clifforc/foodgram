from django.contrib import admin
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.admin import UserAdmin
from django.utils.safestring import mark_safe
from django.urls import reverse

from recipes.models import Favorite, Recipe
from .models import CustomUser, Subscription


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = ("email", "username", "is_active",
                    "is_staff", "is_superuser")
    search_fields = ("email", "username")
    fieldsets = (
        (None, {"fields": ("username", "email", "password")}),
        ("Персональная информация", {"fields": ("first_name", "last_name",
                                                "avatar")}),
        (
            "Подписки и рецепты",
            {"fields": ("get_subscriptions", "get_recipes",
                        "get_favorited_recipes")},
        ),
        ("Разрешения", {"fields": ("is_active", "is_staff", "is_superuser")}),
        ("Важные даты", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "email",
                    "password1",
                    "password2",
                    "is_staff",
                    "is_active",
                ),
            },
        ),
    )
    ordering = ("username",)
    readonly_fields = ("get_subscriptions", "get_recipes",
                       "get_favorited_recipes")

    def get_subscriptions(self, obj):
        custom_user_ct = ContentType.objects.get_for_model(CustomUser)
        app_label = custom_user_ct.app_label
        model_name = custom_user_ct.model

        subscriptions = Subscription.objects.filter(user=obj)
        if subscriptions.exists():
            return mark_safe(
                "<br>".join([
                    f'''<a href="{
                    reverse(f"admin:{app_label}_{model_name}_change",
                            args=[sub.author.id])
                    }">'''
                    f"{sub.author.username}</a>"
                    for sub in subscriptions
                ])
            )
        return "Нет подписок"

    def get_recipes(self, obj):
        recipe_ct = ContentType.objects.get_for_model(Recipe)
        app_label = recipe_ct.app_label
        model_name = recipe_ct.model

        recipes = Recipe.objects.filter(author=obj)
        if recipes.exists():
            return mark_safe(
                "<br>".join([
                    f'''<a href="{
                    reverse(f"admin:{app_label}_{model_name}_change",
                            args=[recipe.id])
                    }">'''
                    f"{recipe.name}</a>"
                    for recipe in recipes
                ])
            )
        return "Нет рецептов"

    def get_favorited_recipes(self, obj):
        recipe_ct = ContentType.objects.get_for_model(Favorite)
        app_label = recipe_ct.app_label
        model_name = recipe_ct.model

        favorited_recipes = Favorite.objects.filter(user=obj)
        if favorited_recipes.exists():
            return mark_safe(
                "<br>".join([
                    f'''<a href="{
                    reverse(f"admin:{app_label}_{model_name}_change",
                            args=[favorited_recipe.id])
                    }">'''
                    f"{favorited_recipe.recipe.name}</a>"
                    for favorited_recipe in favorited_recipes
                ])
            )
        return "Нет избранных рецептов"

    get_subscriptions.short_description = "Подписки"
    get_recipes.short_description = "Рецепты"
    get_favorited_recipes.short_description = "Избранные рецепты"


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("user", "author")
