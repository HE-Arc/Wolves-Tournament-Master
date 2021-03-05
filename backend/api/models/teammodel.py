from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete

class Team(models.Model):
	name = models.CharField(max_length=250)
	image = models.TextField(blank=True)
	leader = models.ForeignKey(User, to_field = "username", on_delete=models.CASCADE)

	def __str__(self):
		return self.name