from django.contrib.auth.models import User
from django.db import models

from core.core import CAN_VOTE, EXTENDED_UG_REGEX, PG_TYPE, UG_TYPE, VoterTypes


class UserProfile(models.Model):
    user = models.OneToOneField(User, related_name='user_profile')
    roll_number = models.CharField(max_length=16)
    user_type = models.CharField(max_length=16, null=True, blank=True)
    voter_type = models.CharField(max_length=16, null=True)

    @property
    def can_vote(self):
        return self.voter_type and self.voter_type.upper() in CAN_VOTE

    @property
    def is_ug(self):
        return self.voter_type and self.voter_type.upper() in UG_TYPE

    @property
    def is_pg(self):
        return self.voter_type and self.voter_type.upper() in PG_TYPE

    def save(self, **kwargs):
        if self.user_type and self.roll_number:
            if self.user_type.upper() in UG_TYPE and EXTENDED_UG_REGEX.match(self.roll_number):
                self.voter_type = VoterTypes.UG
            else:
                self.voter_type = self.user_type.upper()
        return super().save(**kwargs)

    def __str__(self):
        return self.roll_number
