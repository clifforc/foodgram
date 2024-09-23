from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.safestring import mark_safe

from recipes.models import Recipe
from .models import CustomUser, Subscription


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    list_display = (
        'email',
        'username',
        'is_active',
        'is_staff',
        'is_superuser'
    )
    search_fields = (
        'email',
        'username'
    )
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Персональная информация',
         {'fields': ('first_name', 'last_name', 'avatar')}),
        ('Подписки и рецепты',
         {'fields': ('get_subscriptions', 'get_recipes')}),
        ('Разрешения',
         {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Важные даты', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2',
                       'is_staff', 'is_active')
        }),
    )
    ordering = ('username',)
    readonly_fields = ('get_subscriptions', 'get_recipes')

    def get_subscriptions(self, obj):
        subscriptions = Subscription.objects.filter(user=obj)
        if subscriptions:
            return mark_safe('<br>'.join([f'<a href="/admin/users/customuser/{sub.author.id}/change/">{sub.author.username}</a>' for sub in subscriptions]))
        return "Нет подписок"

    def get_recipes(self, obj):
        recipes = Recipe.objects.filter(author=obj)
        if recipes:
            return mark_safe('<br>'.join([f'<a href="/admin/recipes/recipe/{recipe.id}/change/">{recipe.name}</a>' for recipe in recipes]))
        return "Нет рецептов"

    get_subscriptions.short_description = "Подписки"
    get_recipes.short_description = "Рецепты"


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'author'
    )
