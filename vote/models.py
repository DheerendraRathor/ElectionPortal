from django.db import models

from core.core import VOTE_TYPE_CHOICES, VoteTypes
from post.models import Candidate


class VoteSession(models.Model):
    pass


class Vote(models.Model):
    session = models.ForeignKey(VoteSession)
    candidate = models.ForeignKey(Candidate, related_name='votes')
    vote = models.SmallIntegerField(choices=VOTE_TYPE_CHOICES, null=True, blank=True)
    casted_at = models.DateTimeField(auto_now_add=True)
