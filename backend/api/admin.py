from django.contrib import admin
from .models.teammodel import Team
from .models.tournamentmodel import Tournament
from .models.matchmodel import Match

# Register your models here.
admin.site.register(Team)
admin.site.register(Tournament)
admin.site.register(Match)
