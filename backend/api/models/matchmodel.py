from django.db import models
from .teammodel import Team
from .tournamentmodel import Tournament
from django.db.models.signals import post_save, post_delete

class Match(models.Model):
	team1 = models.ForeignKey(Team, related_name = "team1",  on_delete=models.CASCADE)
	team2 = models.ForeignKey(Team, related_name = "team2", on_delete=models.CASCADE)
	tournament = models.ForeignKey(Tournament, on_delete=models.CASCADE)
	score1 = models.IntegerField()
	score2 = models.IntegerField()
	nLap = models.IntegerField()
	posLap = models.IntegerField()

	def __str__(self):
		return self.team1 + " VS " + self.team2