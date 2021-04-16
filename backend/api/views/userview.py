from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action

from django.contrib.auth.models import User
from ..models.teammodel import Team
from ..serializers import UserSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)

    @action(methods=["GET"], detail=True)
    def getteammembers(self, request, pk=None):
        if(pk is not None):
            team = Team.objects.get(id=pk)
            members = team.members.all()
            data = self.get_serializer(members, many=True).data

            return Response(data)
