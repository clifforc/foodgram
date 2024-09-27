from django.contrib.auth import get_user_model
from django.db.models import Exists, OuterRef, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django_filters.rest_framework import DjangoFilterBackend
from djoser.views import UserViewSet
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from users.models import Subscription
from recipes.models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)
from .filters import RecipeFilter
from .pagination import CustomPagination
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    CustomUserCreateSerializer,
    CustomUserSerializer,
    CustomUserSetPasswordSerializer,
    IngredientsSerializer,
    RecipeMiniSerializer,
    RecipeSerializer,
    SubscriptionSerializer,
    TagSerializer,
)

User = get_user_model()


class CustomUserViewSet(UserViewSet):
    """
    ViewSet для управления пользователями.

    Предоставляет стандартные CRUD операции, а также дополнительные действия
    для управления паролем, аватаром и подписками пользователей.
    """

    serializer_class = CustomUserSerializer
    pagination_class = CustomPagination

    def get_permissions(self):
        """
        Разрешения для различных действий.
        """

        if self.action in ["create", "list", "retrieve"]:
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        """
        Возвращает отсортированный QuerySet всех пользователей.
        """

        return User.objects.all().order_by("id")

    def get_serializer_class(self):
        """
        Выбирает соответствующий сериализатор в зависимости от действия.
        """

        if self.action == "create":
            return CustomUserCreateSerializer
        if self.action == "set_password":
            return CustomUserSetPasswordSerializer
        return CustomUserSerializer

    @action(detail=False, methods=["POST"])
    def set_password(self, request):
        """
        Устанавливает новый пароль для аутентифицированного пользователя.
        """

        user = request.user
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        if not user.check_password(serializer.data.get("current_password")):
            return Response(
                "Пароль не соответсвует текущему.",
                status=status.HTTP_400_BAD_REQUEST
            )

        user.set_password(serializer.validated_data["new_password"])
        user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=["PUT", "PATCH", "DELETE"],
        permission_classes=[IsAuthenticated],
        url_path="me/avatar",
    )
    def avatar(self, request):
        """
        Управляет аватаром пользователя.
        """

        user = request.user

        if request.method == "DELETE":
            if user.avatar:
                user.avatar.delete(save=True)
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response("Аватар не найден",
                            status=status.HTTP_404_NOT_FOUND)

        if request.data.get("avatar"):
            serializer = CustomUserSerializer(user, data=request.data,
                                              partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response({"avatar": serializer.data["avatar"]})
            return Response(serializer.errors,
                            status=status.HTTP_400_BAD_REQUEST)
        return Response("Отсутствует поле 'avatar'",
                        status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True, methods=["POST", "DELETE"],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, id=None):
        """
        Управляет подпиской пользователя на автора.
        """

        author = get_object_or_404(User, id=id)
        user = request.user

        if user == author:
            return Response(
                "Вы не можете подписаться на себя.",
                status=status.HTTP_400_BAD_REQUEST
            )

        if request.method == "DELETE":
            subscription = Subscription.objects.filter(user=user,
                                                       author=author)
            if subscription.exists():
                subscription.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                "Вы не подписаны на этого пользователя",
                status=status.HTTP_400_BAD_REQUEST,
            )

        _, created = Subscription.objects.get_or_create(user=user,
                                                        author=author)
        if created:
            recipes_limit = request.query_params.get("recipes_limit")
            serializer = SubscriptionSerializer(
                author, context={"request": request,
                                 "recipes_limit": recipes_limit}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(
            "Вы уже подписаны на этого пользователя",
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(detail=False, methods=["GET"],
            permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        """
        Возвращает список подписок пользователя.
        """

        user = request.user
        queryset = User.objects.filter(subscribed_to__user=user)
        recipes_limit = request.query_params.get("recipes_limit")

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = SubscriptionSerializer(
                page,
                many=True,
                context={"request": request, "recipes_limit": recipes_limit},
            )
            return self.get_paginated_response(serializer.data)
        serializer = SubscriptionSerializer(
            queryset,
            many=True,
            context={"request": request, "recipes_limit": recipes_limit},
        )
        return Response(serializer.data)


class BaseReadOnlyViewset(viewsets.ReadOnlyModelViewSet):
    """
    Базовый класс для ViewSets, предоставляющий только операции чтения.
    """

    permission_classes = [AllowAny]

    def list(self, request):
        """
        Возвращает сериализованный список всех объектов.
        """

        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class TagViewSet(BaseReadOnlyViewset):
    """
    ViewSet для работы с тегами.
    """

    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(BaseReadOnlyViewset):
    """
    ViewSet для работы с ингредиентами.
    """

    queryset = Ingredient.objects.all().order_by("id")
    serializer_class = IngredientsSerializer
    search_fields = ["name"]

    def get_queryset(self):
        """
        Возвращает отфильтрованный QuerySet ингредиентов.
        """

        queryset = super().get_queryset()
        name = self.request.query_params.get("name")
        if name:
            queryset = queryset.filter(name__istartswith=name)
        return queryset


class RecipeViewSet(viewsets.ModelViewSet):
    """
    ViewSet для работы с рецептами.

    Предоставляет CRUD операции для рецептов, а также дополнительные действия
    для работы с корзиной покупок, избранным и получения короткой ссылки.
    """

    queryset = Recipe.objects.all().order_by("-created_at")
    serializer_class = RecipeSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter
    search_fields = ["tags__slug"]

    def get_permissions(self):
        """
        Определяет разрешения для различных действий.
        """

        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAuthenticated(), IsAuthorOrReadOnly()]
        return [AllowAny()]

    def get_queryset(self):
        """
        Возвращает отфильтрованный QuerySet рецептов.
        """

        queryset = super().get_queryset()
        tags = self.request.query_params.getlist("tags")
        author = self.request.query_params.get("author")
        user = self.request.user
        if user.is_authenticated:
            queryset = queryset.annotate(
                is_in_shopping_cart=Exists(
                    ShoppingCart.objects.filter(user=user,
                                                recipe=OuterRef("pk"))
                )
            )
        if tags:
            queryset = queryset.filter(tags__slug__in=tags).distinct()
        if author:
            queryset = queryset.filter(author__id=author)
        return queryset.order_by("id")

    @action(detail=True, methods=["GET"], url_path="get-link")
    def get_short_link(self, request, pk=None):
        """
        Создает и возвращает короткую ссылку на рецепт.
        """

        recipe = self.get_object()
        short_link = recipe.get_or_create_short_link()
        short_url = request.build_absolute_uri(f"/s/{short_link}")
        return Response({"short-link": short_url},
                        status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=["POST", "DELETE"],
        permission_classes=[IsAuthenticated],
        url_path="shopping_cart",
    )
    def shopping_cart(self, request, pk=None):
        """
        Добавляет или удаляет рецепт из корзины покупок.
        """

        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)

        if not user.is_authenticated:
            return Response(
                "Необходимо войти на сайт или зарегистрироваться",
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if request.method == "DELETE":
            try:
                shopping_cart_item = ShoppingCart.objects.get(user=user,
                                                              recipe=recipe)
                shopping_cart_item.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except ShoppingCart.DoesNotExist:
                return Response(
                    "Рецепт не найден в корзине",
                    status=status.HTTP_400_BAD_REQUEST
                )

        _, created = ShoppingCart.objects.get_or_create(user=user,
                                                        recipe=recipe)
        if created:
            serializer = RecipeMiniSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(
            "Рецепт уже добавлен в корзину",
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        detail=False,
        methods=["GET"],
        permission_classes=[IsAuthenticated],
        url_path="download_shopping_cart",
    )
    def download_shopping_cart(self, request):
        """
        Формирует и возвращает список покупок для рецептов в корзине
        пользователя.
        """

        user = request.user
        response = HttpResponse(content_type="text/plain")

        shopping_cart = ShoppingCart.objects.filter(user=user).values_list(
            "recipe", flat=True
        )

        ingredients_sum = (
            RecipeIngredient.objects.filter(recipe__in=shopping_cart)
            .values("ingredient__name", "ingredient__measurement_unit")
            .annotate(total_amount=Sum("amount"))
            .order_by("ingredient__name")
        )

        response.write("Список покупок:\n\n".encode("utf-8"))
        for index, item in enumerate(ingredients_sum, start=1):
            line = (
                f"{index}. {item['ingredient__name']} "
                f"({item['ingredient__measurement_unit']}) - "
                f"{item['total_amount']}\n"
            )
            response.write(line.encode("utf-8"))
        return response

    @action(
        detail=True,
        methods=["POST", "DELETE"],
        permission_classes=[IsAuthenticated],
        url_path="favorite",
    )
    def favorite(self, request, pk=None):
        """
        Добавляет или удаляет рецепт из избранного.
        """

        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)

        if not user.is_authenticated:
            return Response(
                "Необходимо войти на сайт или зарегистрироваться",
                status=status.HTTP_401_UNAUTHORIZED,
            )

        if request.method == "DELETE":
            favorite = Favorite.objects.filter(user=user, recipe=recipe)
            if favorite.exists():
                favorite.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                "Данного рецепта нет в избранном",
                status=status.HTTP_400_BAD_REQUEST
            )

        _, created = Favorite.objects.get_or_create(user=user, recipe=recipe)
        if created:
            serializer = RecipeMiniSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(
            "Рецепт уже добавлен в избранное",
            status=status.HTTP_400_BAD_REQUEST
        )

    def perform_create(self, serializer):
        """
        Выполняет создание рецепта, устанавливая текущего пользователя
        как автора.
        """

        serializer.save(author=self.request.user)


def redirect_short_link(request, short_id):
    """
    Перенаправляет пользователя на страницу рецепта по короткой ссылке.
    """

    recipe = get_object_or_404(Recipe, short_link=short_id)
    return redirect(f"/recipes/{recipe.id}")
