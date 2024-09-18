from django.contrib.auth import get_user_model
from djoser import views as djoser_views

from .serializers import UserSerializer

User = get_user_model()

class UserViewSet(djoser_views.UserViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer