from django.db import models
from post.models import Candidate


class Vote(models.Model):
    candidate = models.ForeignKey(Candidate, related_name='votes')
    yes = models.BooleanField(default=False)
    no = models.BooleanField(default=False)
    neutral = models.BooleanField(default=True)
    casted_at = models.DateTimeField(auto_now_add=True)
