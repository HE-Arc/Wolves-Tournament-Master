from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny

from django.contrib.auth.models import User
from ..models.tournamentmodel import Tournament
from ..serializers import TournamentSerializer


class TournamentViewSet(viewsets.ModelViewSet):
    queryset = Tournament.objects.all()
    serializer_class = TournamentSerializer
    permission_classes = (AllowAny,)

    def create(self, request):
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
