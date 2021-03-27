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
	idInTournament = models.IntegerField() # id of this match inside a tournament
	idParent = models.ForeignKey('self', on_delete=models.CASCADE) # create a many-to-one relationship on itself

	def __str__(self):
		return self.team1 + " VS " + self.team2

		        #         ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                # ('team1', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='team1', to='api.team')),
                # ('team2', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='team2', to='api.team')),
                # ('tournament', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.tournament')),
                # ('score1', models.IntegerField()),
                # ('score2', models.IntegerField()),
                # ('idInTournament', models.IntegerField()),
	            # ('idParent', models.ForeignKey('self', on_delete=models.CASCADE))