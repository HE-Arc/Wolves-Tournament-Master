from rest_framework import routers, serializers, viewsets
from django.contrib.auth.models import User
from .models.teammodel import Team
from .serializers import *
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response


# Create your views here.
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
	
    def post(self, request):
        print("Test post team")

class TeamViewSet(viewsets.ModelViewSet):
	queryset = Team.objects.all()
	# userset = User.objects.select_related().get 
	# queryset = teamset|userset
	# user = User.objects.select_related("leader").get(id = )
	serializer_class = TeamSerializer

