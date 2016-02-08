from django.db import models

from core.core import VOTE_TYPE_CHOICES, VoteTypes
from post.models import Candidate


class Vote(models.Model):
    candidate = models.ForeignKey(Candidate, related_name='votes')
    vote = models.SmallIntegerField(choices=VOTE_TYPE_CHOICES, default=VoteTypes.NEUTRAL)
    casted_at = models.DateTimeField(auto_now_add=True)
