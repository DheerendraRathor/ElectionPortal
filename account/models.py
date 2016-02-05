from django.contrib.auth.models import User
from django.db import models

from core.core import CAN_VOTE, PG_TYPE, UG_TYPE


class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name='user_profile')
    roll_number = models.CharField(max_length=16)
    user_type = models.CharField(max_length=16, null=True, blank=True)

    @property
    def can_vote(self):
        return self.user_type and self.user_type.upper() in CAN_VOTE

    @property
    def is_ug(self):
        return self.user_type.upper() in UG_TYPE

    @property
    def is_pg(self):
        return self.user_type.upper() in PG_TYPE
