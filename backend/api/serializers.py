from rest_framework import serializers
from django.contrib.auth.models import User
from .models.teammodel import Team
from rest_framework.authtoken.models import Token

# Serializers define the API representation.
class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ['url', 'id', 'username', 'email', 'is_staff']

class TeamSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Team
        fields = ['url', 'id', 'name', 'image', 'leader']