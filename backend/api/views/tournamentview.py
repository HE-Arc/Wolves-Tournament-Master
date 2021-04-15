from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, AllowAny

from ..models.tournamentmodel import Tournament
from ..serializers import TournamentSerializer


class TournamentViewSet(viewsets.ModelViewSet):
    queryset = Tournament.objects.all()
    serializer_class = TournamentSerializer
    permission_classes = (AllowAny,)
