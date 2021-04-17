from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action

from django.contrib.auth.models import User
from ..models.tournamentmodel import Tournament
from ..models.teammodel import Team
from ..models.notificationmodel import Notification
from ..serializers import TournamentSerializer
from ..serializers import TeamSerializer

class TournamentViewSet(viewsets.ModelViewSet):
    queryset = Tournament.objects.all()
    serializer_class = TournamentSerializer
    permission_classes = (AllowAny,)

    def create(self, request):
        """
            Create a new tournament.
        """
        permission_classes = (IsAuthenticated,)

        data = request.data

        serializer = self.serializer_class(
            data=data, context={'request': request})
        serializer.is_valid(raise_exception=True)

        if serializer.is_valid():
            tournament = Tournament.objects.create(**serializer.validated_data)

            for referee in data["referees"]:
                user = User.objects.get(id=referee)
                tournament.referees.add(user)

            tournament.save()

            return Response(self.get_serializer(tournament).data, status=status.HTTP_200_OK)
        else:
            response = {
                "message": "unable to create tournament"
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)


    @action(methods=["POST"], detail=True)
    def addTeam(self, request, pk=None):
        """
            Add a team to a tournament.
            The tournament id is the pk parameter.
            The team id is passed in the request with the field "teamid"
        """
        permission_classes = (IsAuthenticated,)
        
        if "teamid" in request.data and pk is not None:

            team = Team.objects.get(id=request.data["teamid"])
            tournament = Tournament.objects.get(pk=int(pk))
            tournament.teams.add(team)

            # send a notification to every memeber of the team
            for member in team.members.all():
                notification = Notification(
                        message= f"""Your team {team.name} participates to the tournament {tournament.name} 
                                    of {tournament.gameName} the {tournament.deadLineDate}.""",
                        seen=False,
                        notificationType="MESSAGE",
                        user=member,
                        team=team)

                notification.save()


            return Response(TeamSerializer(team, context={'request': request}).data, status=status.HTTP_200_OK)
        else:
            response = {
                "message": "can't add team"
            }
            return Response(response, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=["GET"], detail=False)
    def tournamentsforhome(self, request, pk=None):

        """
            Return every tournament with specific attributes added : 
              * isLeader : true if the logged user is the leader of at least one 
                           team which participate to the tournament
              * isParticipating : true if at least one of the logged user team
                           is participating to the tournament
              * isDeadLineOver : true if the tournament registration deadline has been reached

        """
        from datetime import date
        
        tournaments = Tournament.objects.all()
        teamQueryset = Team.objects.all()
        response = []
        userId = self.request.query_params.get("uid", None)

        for tournament in tournaments:
            loggedUser = None
            if userId is not None and userId.isnumeric():
                loggedUser = User.objects.all().get(pk=userId)
            teams = teamQueryset.filter(tournament__id=tournament.id)

            isLeader = False
            try:
                isLeader = len(teamQueryset.filter(leader=loggedUser)) > 0
            except:
                pass

            isParticipating = False
            try:
                isParticipating = len(teams.filter(members__id=loggedUser.id)) > 0
            except:
                pass

            isDeadLineOver = tournament.deadLineDate < date.today()
            
            data = self.get_serializer(tournament).data
            data["isLeader"] = isLeader
            data["isParticipating"] = isParticipating
            data["isDeadLineOver"] = isDeadLineOver

            response.append(data)

        return Response(response, status=status.HTTP_200_OK)