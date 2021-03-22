from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete
from .teammodel import Team

class Notification(models.Model):
	message = models.CharField(max_length=1000)
	seen = models.BooleanField(default=False)
	notificationType = models.CharField(max_length=20, default="MESSAGE")
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	team = models.ForeignKey(Team, on_delete=models.CASCADE, null=True)

	def __str__(self):
		return self.name