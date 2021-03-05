from rest_framework import routers, serializers, viewsets
from django.contrib.auth.models import User
from .models.teammodel import Team
from .serializers import *


# Create your views here.
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class TeamViewSet(viewsets.ModelViewSet):
	queryset = Team.objects.all()
	serializer_class = TeamSerializer
