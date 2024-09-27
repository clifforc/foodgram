from django_filters.rest_framework import BooleanFilter, FilterSet

from ..recipes.models import Recipe


class RecipeFilter(FilterSet):
    """
    Набор фильтров для модели Recipe.

    Позволяет фильтровать рецепты по следующим критериям:
    - наличие в списке покупок текущего пользователя
    - наличие в избранном текущего пользователя
    """

    is_in_shopping_cart = BooleanFilter(method="filter_is_in_shopping_cart")
    is_favorited = BooleanFilter(method="filter_is_favorited")

    class Meta:
        model = Recipe
        fields = ["is_in_shopping_cart", "is_favorited"]

    def filter_is_in_shopping_cart(self, queryset, name, value):
        """
        Фильтрует рецепты по наличию в списке покупок текущего пользователя.
        """

        user = self.request.user
        if user.is_authenticated and value:
            return queryset.filter(in_shopping_cart__user=user)
        return queryset

    def filter_is_favorited(self, queryset, name, value):
        """
        Фильтрует рецепты по наличию в избранном текущего пользователя.
        """

        user = self.request.user
        if user.is_authenticated and value:
            return queryset.filter(favorited_by__user=user)
        return queryset
