from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.safestring import mark_safe

from recipes.models import Recipe, Favorite
from .models import CustomUser, Subscription


@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    """
    Настройки интерфейса администратора для модели CustomUser.
    """

    list_display = ('email','username','is_active','is_staff','is_superuser')
    search_fields = ('email','username')
    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Персональная информация',
         {'fields': ('first_name', 'last_name', 'avatar')}),
        ('Подписки и рецепты',
         {'fields': ('get_subscriptions', 'get_recipes', 'get_favorited_recipes')}),
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
    readonly_fields = ('get_subscriptions',
                       'get_recipes',
                       'get_favorited_recipes')

    def get_subscriptions(self, obj: CustomUser) -> str:
        """
        Получить список подписок пользователя.

        Args:
            obj (CustomUser): Объект пользователя.

        Returns:
            str: HTML-строка со ссылками на авторов, на которых подписан пользователь,
                 или сообщение об отсутствии подписок.
        """

        subscriptions = Subscription.objects.filter(user=obj)
        if subscriptions:
            return mark_safe('<br>'.join(['<a href="/admin/users/customuser/'
                                          f'{sub.author.id}/change/">'
                                          f'{sub.author.username}</a>'
                                          for sub in subscriptions]))
        return "Нет подписок"

    def get_recipes(self, obj: CustomUser) -> str:
        """
        Получить список рецептов пользователя.

        Args:
            obj (CustomUser): Объект пользователя.

        Returns:
            str: HTML-строка со ссылками на рецепты пользователя,
                 или сообщение об отсутствии рецептов.
        """

        recipes = Recipe.objects.filter(author=obj)
        if recipes:
            return mark_safe(
                '<br>'.join(['<a href="/admin/recipes/recipe/'
                             f'{recipe.id}/change/">{recipe.name}</a>'
                             for recipe in recipes]))
        return "Нет рецептов"

    def get_favorited_recipes(self, obj: CustomUser) -> str:
        """
        Получить список избранных рецептов пользователя.

        Args:
            obj (CustomUser): Объект пользователя.

        Returns:
            str: HTML-строка со ссылками на избранные рецепты пользователя,
                 или сообщение об отсутствии избранных рецептов.
        """

        favorited_recipes = Favorite.objects.filter(user=obj)
        if favorited_recipes:
            return mark_safe(
                '<br>'.join(['<a href="/admin/recipes/favorite/'
                             f'{favorited_recipe.id}/change/">'
                             f'{favorited_recipe.recipe.name}</a>'
                             for favorited_recipe in favorited_recipes]))
        return "Нет избранных рецептов"

    get_subscriptions.short_description = "Подписки"
    get_recipes.short_description = "Рецепты"
    get_favorited_recipes.short_description = "Избранные рецепты"


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    """
    Настройки интерфейса администратора для модели Subscription.
    """

    list_display = ('user','author')
