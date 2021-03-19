from rest_framework import serializers
from django.contrib.auth.models import User
from .models.teammodel import Team
from .models.matchmodel import Match
from .models.tournamentmodel import Tournament
from .models.notificationmodel import Notification
from rest_framework.authtoken.models import Token

# Serializers define the API representation.
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'id', 'username', 'email', 'password']
        extra_kwargs = {'password':{'required':True, 'write_only':True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        Token.objects.create(user=user)
        return user

class TeamSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Team
        fields = ['url', 'id', 'name', 'image', 'leader']

class MatchSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Match
        fields = ['url', 'id', 'team1', 'team2', 'tournament', 'score1', 'score2', 'nLap', 'posLap']

class TournamentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Tournament
        fields = ['url', 'id', 'organizer', 'name', 'gameName', 'matchDuration', 'breakDuration', 'deadLineDate', 'nbTeam']

class NotificationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Notification
        fields = ['url', 'id', 'user', 'seen', 'message']