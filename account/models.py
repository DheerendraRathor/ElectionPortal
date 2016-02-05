from django.db import models
from django.contrib.auth.models import User


class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name='user_profile')
    roll_number = models.CharField(max_length=16)
    user_type = models.CharField(max_length=16, null=True, blank=True)
