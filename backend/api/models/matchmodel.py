from django.db import models
from django.contrib.auth.models import Team
from django.db.models.signals import post_save, post_delete

class Match(models.Model):
	team1 = models.ForeignKey(Team, to_field = "name", on_delete=models.CASCADE)
	team2 = models.ForeignKey(Team, to_field = "name", on_delete=models.CASCADE)
	#tournament = models.ForeignKey(Team, to_field = "name", on_delete=models.CASCADE)
	score1 = models.IntegerField()
	score1 = models.IntegerField()
	nLap = models.IntegerField()
	posLap = models.IntegerField()

	def __str__(self):
		return self.team1 + " VS " + self.team2