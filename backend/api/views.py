from rest_framework import routers, serializers, viewsets
from django.contrib.auth.models import User
from .models.teammodel import Team
from .models.matchmodel import Match
from .models.tournamentmodel import Tournament
from .models.notificationmodel import Notification
from .serializers import *
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework import status


# Create your views here.
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (AllowAny,)
    # authentication_classes = (TokenAuthentication,)
    # permission_classes = (IsAuthenticated,)


class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    # userset = User.objects.select_related().get
    # queryset = teamset|userset
    # user = User.objects.select_related("leader").get(id = )
    serializer_class = TeamSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (AllowAny,)

    @action(methods=["POST"], detail=True)
    def adduser(self, request, pk=None):
        if "userid" and "notificationid" in request.data:
            notification = Notification.objects.get(
                id=request.data["notificationid"])
            userid = request.data["userid"]
            if notification.user.id == userid and notification.team.id == int(pk):
                user = User.objects.get(id=userid)
                team = Team.objects.get(id=pk)
                team.members.add(user)
                notification.seen = True
                notification.message = "[Accepté] " + notification.message
                notification.notificationType = "MESSAGE"
                notification.save()
                response = {
                    "message": "user added successfuly"
                }
                return Response(response, status=status.HTTP_200_OK)
            else:
                response = {
                    "message": "you not allowed to join this team"
                }
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
        else:
            response = {
                "message": "can't add user"
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

    # def get_queryset(self):
    #     queryset = Team.objects.all()
    #     uid = self.request.query_params.get("uid", None)
    #     if(uid is not None):
    #         queryset = queryset.filter(members=uid)
    #         return queryset


class MatchViewSet(viewsets.ModelViewSet):
    queryset = Match.objects.all()
    serializer_class = MatchSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (AllowAny,)


class TournamentViewSet(viewsets.ModelViewSet):
    queryset = Tournament.objects.all()
    serializer_class = TournamentSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (AllowAny,)


class NotificationViewSet(viewsets.ModelViewSet):
    queryset = Notification.objects.all()
    serializer_class = NotificationSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (AllowAny,)

    # Get all notification by user id

    def get_queryset(self):
        queryset = Notification.objects.all()
        uid = self.request.query_params.get("uid", None)
        if(uid is not None):
            queryset = queryset.filter(user=uid)
            #queryset = queryset.filter(seen=False)
        return queryset


class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        token, created = Token.objects.get_or_create(user=user)
        return Response({
            'token': token.key,
            'user_id': user.pk,
            'name': user.username,
            'email': user.email
        })
