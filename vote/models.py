from django.db import models

from core.core import VOTE_TYPE_CHOICES, VoteTypes
from post.models import Candidate


class VoteSession(models.Model):
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.timestamp)


class Vote(models.Model):
    session = models.ForeignKey(VoteSession, related_name='votes')
    candidate = models.ForeignKey(Candidate, related_name='votes')
    vote = models.SmallIntegerField(choices=VOTE_TYPE_CHOICES, null=True, blank=True)
