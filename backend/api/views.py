import base64

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.db.models import Exists, OuterRef, Sum
from django.shortcuts import get_object_or_404, redirect
from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse
from djoser.views import UserViewSet
from rest_framework import status, viewsets, filters
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
import shortuuid

from .serializers import (CustomUserCreateSerializer, CustomUserSerializer,
                          CustomUserSetPasswordSerializer, TagSerializer,
                          IngredientsSerializer, RecipeSerializer,
                          SubscriptionSerializer, RecipeMiniSerializer)
from .pagination import CustomPagination
from .permissions import IsAuthorOrReadOnly
from .filters import RecipeFilter
from recipes.models import Tag, Ingredient, Recipe, ShoppingCart, RecipeIngredient, Favorite
from users.models import Subscription


User = get_user_model()


class CustomUserViewSet(UserViewSet):
    serializer_class = CustomUserSerializer
    pagination_class = CustomPagination

    def get_permissions(self):
        if self.action in ['create', 'list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        return User.objects.all().order_by('id')

    def get_serializer_class(self):
        if self.action == 'create':
            return CustomUserCreateSerializer
        if self.action == 'set_password':
            return CustomUserSetPasswordSerializer
        return CustomUserSerializer

    @action(detail=False, methods=['POST'], permission_classes=[IsAuthenticated])
    def set_password(self, request):
        user = request.user
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            if not user.check_password(serializer.data.get("current_password")):
                return Response({"current_password": ["Пароль не соответсвует текущему."]}, status=status.HTTP_400_BAD_REQUEST)
            user.set_password(serializer.data.get("new_password"))
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False,
            methods=['PUT', 'PATCH', 'DELETE'],
            permission_classes=[IsAuthenticated],
            url_path='me/avatar')
    def avatar(self, request):
        avatar = request.user.avatar

        if request.method == 'DELETE':
            if not avatar:
                return Response("Аватар не найден", status=status.HTTP_400_BAD_REQUEST)
            avatar.delete(save=True)
            return Response(status=status.HTTP_204_NO_CONTENT)

        avatar_data = request.data.get('avatar')
        if not avatar_data:
            return Response("Отсутствует поле 'avatar'",status=status.HTTP_400_BAD_REQUEST)

        avatar_format, avatar_base64 = avatar_data.split(';base64,')
        extension = avatar_format.split('/')[-1]
        filename = f"{request.user.username}_avatar.{extension}"
        data = ContentFile(base64.b64decode(avatar_base64), name=filename)

        avatar.save(filename, data)
        return Response({'avatar': request.user.avatar.url}, status=status.HTTP_200_OK)

    @action(detail=True,
            methods=['POST', 'DELETE'],
            permission_classes=[IsAuthenticated])
    def subscribe(self, request, id=None):
        author = get_object_or_404(User, id=id)
        user = request.user

        if user == author:
            return Response("Вы не можете подписаться на себя.", status=status.HTTP_400_BAD_REQUEST)

        if request.method == 'DELETE':
            subscription = Subscription.objects.filter(user=user, author=author)
            if subscription.exists():
                subscription.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response("Вы не подписаны на этого пользователя", status=status.HTTP_400_BAD_REQUEST)

        _, created = Subscription.objects.get_or_create(user=user, author=author)
        if created:
            recipes_limit = request.query_params.get('recipes_limit')
            serializer = SubscriptionSerializer(
                author,
                context={'request': request, 'recipes_limit': recipes_limit}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response("Вы уже подписаны на этого пользователя", status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False,
            methods=['GET'],
            permission_classes=[IsAuthenticated])
    def subscriptions(self, request):
        user = request.user
        queryset = User.objects.filter(subscribed_to__user=user)

        recipes_limit = request.query_params.get('recipes_limit')

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = SubscriptionSerializer(
                page,
                many=True,
                context={'request': request, 'recipes_limit': recipes_limit})
            return self.get_paginated_response(serializer.data)
        serializer = SubscriptionSerializer(
            page,
            many=True,
            context={'request': request, 'recipes_limit': recipes_limit})
        return Response(serializer.data)

class BaseReadOnlyViewset(viewsets.ReadOnlyModelViewSet):
    permission_classes = [AllowAny]

    def list(self, request):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)


class TagViewSet(BaseReadOnlyViewset):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class IngredientViewSet(BaseReadOnlyViewset):
    queryset = Ingredient.objects.all().order_by('id')
    serializer_class = IngredientsSerializer
    search_fields = ['name']

    def get_queryset(self):
        queryset = super().get_queryset()
        name = self.request.query_params.get('name')
        if name:
            queryset = queryset.filter(name__istartswith=name)
        return queryset


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all().order_by('id')
    serializer_class = RecipeSerializer
    pagination_class = CustomPagination
    # filter_backends = [filters.SearchFilter]
    filter_backends = [DjangoFilterBackend]
    filterset_class = RecipeFilter
    search_fields = ['tags__slug']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAuthenticated(), IsAuthorOrReadOnly()]
        return [AllowAny()]

    def get_queryset(self):
        queryset = super().get_queryset()
        tags = self.request.query_params.getlist('tags')
        author = self.request.query_params.get('author')
        user = self.request.user
        if user.is_authenticated:
            queryset = queryset.annotate(
                is_in_shopping_cart=Exists(
                    ShoppingCart.objects.filter(
                        user=user,
                        recipe=OuterRef('pk')
                    )
                )
            )
        if tags:
            queryset = queryset.filter(tags__slug__in=tags).distinct()
        if author:
            queryset = queryset.filter(author__id=author)
        return queryset.order_by('id')

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

    @action(detail=True,
            methods=['GET'],
            url_path='get-link')
    def get_short_link(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        short_id = shortuuid.uuid()[:8]
        recipe.short_link = short_id
        recipe.save()
        short_url = request.build_absolute_uri(f'/s/{short_id}')
        return Response({'short-link': short_url}, status=status.HTTP_200_OK)

    @action(detail=True,
            methods=['POST','DELETE'],
            permission_classes=[IsAuthenticated],
            url_path='shopping_cart')
    def shopping_cart(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)

        if not user.is_authenticated:
            return Response("Необходимо войти на сайт или зарегистрироваться", status=status.HTTP_401_UNAUTHORIZED)

        if request.method == 'DELETE':
            try:
                shopping_cart_item = ShoppingCart.objects.get(user=user, recipe=recipe)
                shopping_cart_item.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            except ShoppingCart.DoesNotExist:
                return Response("Рецепт не найден в корзине",
                                status=status.HTTP_400_BAD_REQUEST)

        _, created = ShoppingCart.objects.get_or_create(user=user, recipe=recipe)
        if created:
            serializer = RecipeMiniSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response("Рецепт уже добавлен в корзину", status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False,
            methods=["GET"],
            permission_classes=[IsAuthenticated],
            url_path='download_shopping_cart')
    def download_shopping_cart(self, request):
        user = request.user
        response = HttpResponse(content_type='text/plain')
        response['Content-Disposition'] = f'attachment; filename="{user.username}_shopping_cart.txt"'

        shopping_cart = ShoppingCart.objects.filter(user=user).values_list('recipe', flat=True)

        igredients_sum = (((RecipeIngredient.objects.filter(recipe__in=shopping_cart)
                          .values('ingredient__name', 'ingredient__measurement_unit'))
                          .annotate(total_amount=Sum('amount')))
                          .order_by('ingredient__name'))

        for item in igredients_sum:
            line = f"{item['ingredient__name']} ({item['ingredient__measurement_unit']}) - {item['total_amount']}\n"
            response.write(line)

        return response

    @action(detail=True,
            methods=['POST','DELETE'],
            permission_classes=[IsAuthenticated],
            url_path='favorite')
    def favorite(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)

        if not user.is_authenticated:
            return Response("Необходимо войти на сайт или зарегистрироваться",
                            status=status.HTTP_401_UNAUTHORIZED)

        if request.method == 'DELETE':
            favorite = Favorite.objects.filter(user=user, recipe=recipe)
            if favorite.exists():
                favorite.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response("Данного рецепта нет в избранном", status=status.HTTP_400_BAD_REQUEST)

        _, created = Favorite.objects.get_or_create(user=user, recipe=recipe)
        if created:
            serializer = RecipeMiniSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response("Рецепт уже добавлен в избранное", status=status.HTTP_400_BAD_REQUEST)


    def process_image(self, image_data):
        if image_data and isinstance(image_data, str) and image_data.startswith('data:image'):
            image_format, image_base64 = image_data.split(';base64,')
            extension = image_format.split('/')[-1]
            filename = f'recipe_image.{extension}'
            return ContentFile(base64.b64decode(image_base64), name=filename)
        return image_data

    def create(self, request, *args, **kwargs):
        image_data = request.data.get('image')
        request.data['image'] = self.process_image(image_data)
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        image_data = request.data.get('image')
        request.data['image'] = self.process_image(image_data)
        return super().update(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)


def redirect_short_link(request, short_id):
    recipe = get_object_or_404(Recipe, short_link=short_id)
    return redirect('api:recipe-detail', pk=recipe.pk)