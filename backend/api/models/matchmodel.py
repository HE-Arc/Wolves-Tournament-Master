from django.db import models
from .teammodel import Team
from .tournamentmodel import Tournament
from django.db.models.signals import post_save, post_delete
from .teammodel import Team


class Match(models.Model):
    # blank = True for form validation and null=true for database nullable
    team1 = models.ForeignKey(Team, related_name="team1", on_delete=models.CASCADE, blank=True, null=True)
    team2 = models.ForeignKey(Team, related_name="team2", on_delete=models.CASCADE, blank=True, null=True)
    tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
    score1 = models.IntegerField(blank=True, null=True)
    score2 = models.IntegerField(blank=True, null=True)
    idInTournament = models.IntegerField()  # id of this match inside a tournament
    # idInTournament of the parent
    idParent = models.IntegerField(blank=True, null=True)

    def __str__(self):
        team1 = self.team1.name if self.team1 is not None else "tbd"  # to be defined
        team2 = self.team2.name if self.team2 is not None else "tbd"

        return team1 + " VS " + team2
