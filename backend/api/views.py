import base64
import os

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .serializers import UserCreateSerializer, UserSerializer, UserSetPasswordSerializer
from .pagination import CustomPagination

User = get_user_model()


class UserViewSet(UserViewSet):
    serializer_class = UserSerializer
    pagination_class = CustomPagination

    def get_permissions(self):
        if self.action in ['create', 'list', 'retrieve']:
            return [AllowAny()]
        return [IsAuthenticated()]

    def get_queryset(self):
        return User.objects.all().order_by('id')

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        if self.action == 'set_password':
            return UserSetPasswordSerializer
        return UserSerializer

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
                return Response({"error": "Аватар не найден"},
                                status=status.HTTP_400_BAD_REQUEST)
            avatar.delete(save=True)
            return Response({"message": "Аватар удалён"},
                            status=status.HTTP_204_NO_CONTENT)
        avatar_data = request.data.get('avatar')
        if not avatar_data:
            return Response({"error": "Отсутствует поле 'avatar'"},
                                status=status.HTTP_400_BAD_REQUEST)
        avatar_format, avatar_base64 = avatar_data.split(';base64,')
        extension = avatar_format.split('/')[-1]
        filename = f"{request.user.username}_avatar.{extension}"
        data = ContentFile(base64.b64decode(avatar_base64), name=filename)
        if avatar:
            avatar.delete()
        avatar.save(filename, data, save=True)
        return Response({'avatar': request.user.avatar.url},
                        status=status.HTTP_200_OK)
