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

    @action(methods=["GET"], detail=True)
    def getteammembers(self, request, pk=None):
        if(pk is not None):
            team = Team.objects.get(id=pk)
            members = team.members.all()
            data = self.get_serializer(members, many=True).data

            return Response(data)

class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    # userset = User.objects.select_related().get
    # queryset = teamset|userset
    # user = User.objects.select_related("leader").get(id = )
    serializer_class = TeamSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (AllowAny,)

    @action(methods=["POST"], detail=True)
    def removeuser(self, request, pk=None):
        if "userid" in request.data:
            userid = request.data["userid"]
            user = User.objects.get(id=userid)
            team = Team.objects.get(id=pk)

            notification = Notification(message = "you have been fired from " + team.name,
            seen = False,
            notificationType = "MESSAGE",
            user = user,
            team = team)
            notification.save()

            team.members.remove(user)
            response = {
                    "message": "user removed successfuly"
                }
            return Response(response, status=status.HTTP_200_OK)

        else:
            response = {
                "message": "you can't remove this user"
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)
            
        

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
                notification.message = "[Accepted] " + notification.message
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

    @action(methods=["GET"], detail=True)
    def getteamsbymember(self, request, pk=None):
        if(pk is not None):
            teams = Team.objects.filter(members__id=pk)
            data = self.get_serializer(teams, many=True).data
            return Response(data)

    @action(methods=["GET"], detail=False)
    def getteamsbytournament(self, request, pk=None):
        queryset = Team.objects.all()
        # get every team which participates to the tournament with id=tid
        tid = request.query_params.get("tid", None)
        
        if(tid is not None):
            tournament = Tournament.objects.filter(pk=tid)
            teams = queryset.filter(tournament__in=tournament)
            data = self.get_serializer(teams, many=True).data
            return Response(data)

        return Response({"message": "tid is not defined"})

class MatchViewSet(viewsets.ModelViewSet):
    queryset = Match.objects.all()
    serializer_class = MatchSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (AllowAny,)

    @action(methods=["GET"], detail=False)
    def getmatchsbytournament(self, request, pk=None):
        queryset = Match.objects.all()
        tid = self.request.query_params.get("tid", None)

        # get all matches of a tournament
        if(tid is not None):
            matchs = queryset.filter(tournament=tid)
            data = self.get_serializer(matchs, many=True).data
            return Response(data)

        return Response({"message": "tid is not defined"})
 
    @action(methods=["PUT"], detail=True)
    def updatematchscores(self, request, pk=None):
        queryset = Match.objects.all()
        data = request.data

        if pk is not None:
            serializer = self.serializer_class(data=data, context={'request': request})
            serializer.is_valid(raise_exception=True)
            
            if serializer.is_valid():
                # match = serializer.validated_data['match']
                # match, created = queryset.filter(pk=data["id"]).update_or_create(serializer.validated_data)
                match, created = queryset.filter(pk=pk).update_or_create(serializer.validated_data)
                
                ## update parent
                if match.idParent is not None:
                    #parent = queryset.get(pk=int(match.idParent))
                    parent = queryset.filter(tournament=match.tournament).filter(idInTournament=int(match.idParent))[0]

                    if parent.team1 is None:
                        parent.team1 = match.team1 if match.score1 > match.score2 else match.team2
                    else:
                        parent.team2 = match.team1 if match.score1 > match.score2 else match.team2

                    # parent, created = queryset.filter(pk=match.idParent).update_or_create(parent)
                    parent.save()
                                    
                return Response(self.get_serializer(match).data, status=status.HTTP_200_OK)
            else:
                response = {
                    "message": "unable to update match"
                }
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
    
class TournamentViewSet(viewsets.ModelViewSet):
    queryset = Tournament.objects.all()
    serializer_class = TournamentSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (AllowAny,)

    @action(methods=["GET"], detail=True)
    def gettournamentproperties(self, request, pk=None):

        if pk is not None:
            queryset = Tournament.objects.all()
            tournament = queryset.get(pk=int(pk))

            return Response(self.get_serializer(tournament).data, status=status.HTTP_200_OK)

    @action(methods=["GET"], detail=False)
    def tournamentsforhome(self, request, pk=None):
        from datetime import date

        tournaments = Tournament.objects.all()

        teamQueryset = Team.objects.all()

        response = []

        for tournament in tournaments:
            # TODO : get logged user and check if he participates and if he's
            # the team leader
            userId = 2
            loggedUser = User.objects.all().get(pk=userId)
            teams = teamQueryset.filter(tournament__id=tournament.id)

            isLeader = False
            try:
                isLeader = len(teamQueryset.filter(leader=loggedUser)) > 0
            except User.DoesNotExist:
                pass

            isParticipating = False
            try:
                isParticipating = len(teams.filter(members__id=loggedUser.id)) > 0
            except User.DoesNotExist:
                pass

            isDeadLineOver = tournament.deadLineDate < date.today()
            
            data = self.get_serializer(tournament).data
            data["isLeader"] = isLeader
            data["isParticipating"] = isParticipating
            data["isDeadLineOver"] = isDeadLineOver

            response.append(data)

        return Response(response, status=status.HTTP_200_OK)


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
