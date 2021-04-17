from rest_framework import status, viewsets
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.decorators import action

from ..models.matchmodel import Match
from ..serializers import MatchSerializer


class MatchViewSet(viewsets.ModelViewSet):
    queryset = Match.objects.all()
    serializer_class = MatchSerializer
    permission_classes = (AllowAny,)

    @action(methods=["GET"], detail=False)
    def getmatchsbytournament(self, request, pk=None):
        """
            Get all matches of a tournament.
            The tournament id is passed as GET parameter
        """
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
        """
            Update a match score1 and score2 fields. 
            If the matchs has a parent node in the tournament brackets,
            it's parent team1 or team2 is udpated automatically.
        """
        permission_classes = (IsAuthenticated,)

        queryset = Match.objects.all()
        data = request.data

        if pk is not None:

            serializer = self.serializer_class(
                data=data, context={'request': request})
            serializer.is_valid(raise_exception=True)

            if serializer.is_valid():
                match, created = queryset.filter(pk=pk).update_or_create(serializer.validated_data)
                
                print("idInTournament = ", match.idInTournament)

                # update parent
                if match.idParent is not None:
                    parent = queryset.filter(tournament=match.tournament).filter(
                        idInTournament=int(match.idParent))[0]
                    
                    if parent.idInTournament * 2 == match.idInTournament:
                        parent.team1 = match.team1 if match.score1 > match.score2 else match.team2
                    else:
                        parent.team2 = match.team1 if match.score1 > match.score2 else match.team2

                    parent.save()

                return Response(self.get_serializer(match).data, status=status.HTTP_200_OK)
            else:
                response = {
                    "message": "unable to update match"
                }
                return Response(response, status=status.HTTP_400_BAD_REQUEST)
