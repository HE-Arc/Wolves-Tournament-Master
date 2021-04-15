from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action

from django.contrib.auth.models import User
from ..models.teammodel import Team
from ..models.notificationmodel import Notification
from ..models.tournamentmodel import Tournament
from ..serializers import TeamSerializer


class TeamViewSet(viewsets.ModelViewSet):
    queryset = Team.objects.all()
    # userset = User.objects.select_related().get
    # queryset = teamset|userset
    # user = User.objects.select_related("leader").get(id = )
    serializer_class = TeamSerializer
    permission_classes = (AllowAny,)

    @action(methods=["POST"], detail=True)
    def removeuser(self, request, pk=None):
        if "userid" in request.data:
            userid = request.data["userid"]
            user = User.objects.get(id=userid)
            team = Team.objects.get(id=pk)

            notification = Notification(message="you have been fired from " + team.name,
                                        seen=False,
                                        notificationType="MESSAGE",
                                        user=user,
                                        team=team)
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
        permission_classes = (IsAuthenticated,)

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
