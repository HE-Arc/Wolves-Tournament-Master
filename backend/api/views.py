from rest_framework import routers, serializers, viewsets
from django.contrib.auth.models import User
from .models.teammodel import Team
from .serializers import *
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import TokenAuthentication


# Create your views here.
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)
    # authentication_classes = (TokenAuthentication,)
    # permission_classes = (IsAuthenticated,)
	
    def post(self, request):
        print("Test post team")

class TeamViewSet(viewsets.ModelViewSet):
	queryset = Team.objects.all()
	# userset = User.objects.select_related().get 
	# queryset = teamset|userset
	# user = User.objects.select_related("leader").get(id = )
	serializer_class = TeamSerializer
	authentication_classes = (TokenAuthentication,)
	permission_classes = (AllowAny,)

# class CustomAuthToken(ObtainAuthToken):
#     def post(self, request, *args, **kwargs):
#         serializer = self.serializer_class(data=request.data,
#                                            context={'request': request})
#         serializer.is_valid(raise_exception=True)
#         user = serializer.validated_data['user']
#         token, created = Token.objects.get_or_create(user=user)
#         return Response({
#             'token': token.key,
#             'user_id': user.pk,
#             'email': user.email
#         })