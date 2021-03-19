from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save, post_delete

class Notification(models.Model):
	message = models.CharField(max_length=1000)
	seen = models.BooleanField(default=False)
	user = models.ForeignKey(User, to_field = "username", on_delete=models.CASCADE)

	def __str__(self):
		return self.name