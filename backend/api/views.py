import base64
import uuid

from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .serializers import UserCreateSerializer, UserSerializer
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
        return UserSerializer

    @action(detail=False, methods=['GET', 'PUT'], url_path='me')
    def me(self, request):
        if request.method == 'GET':
            serializer = self.get_serializer(request.user)
            return Response(serializer.data)
        elif request.method == 'PUT':
            serializer = self.get_serializer(request.user, data=request.data,
                                             partial=True)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

    @action(detail=False, methods=['GET', 'PUT'], url_path='me/avatar',
            permission_classes=[IsAuthenticated])
    def update_avatar(self, request):
        if request.method == 'GET':
            return Response({
                                'avatar': request.user.avatar.url if request.user.avatar else None})

        if 'avatar' not in request.data:
            return Response({'error': 'No avatar provided'},
                            status=status.HTTP_400_BAD_REQUEST)

        avatar_data = request.data['avatar']
        if not avatar_data.startswith('data:image'):
            return Response({'error': 'Invalid image data'},
                            status=status.HTTP_400_BAD_REQUEST)

        format, imgstr = avatar_data.split(';base64,')
        ext = format.split('/')[-1]
        filename = f"{uuid.uuid4()}.{ext}"
        data = ContentFile(base64.b64decode(imgstr), name=filename)

        if request.user.avatar:
            request.user.avatar.delete()

        request.user.avatar.save(filename, data, save=True)

        return Response({'avatar': request.user.avatar.url},
                        status=status.HTTP_200_OK)

    @action(detail=False, methods=['DELETE'], url_path='me/avatar')
    def delete_avatar(self, request):
        request.user.avatar.delete(save=True)
        return Response(status=status.HTTP_204_NO_CONTENT)