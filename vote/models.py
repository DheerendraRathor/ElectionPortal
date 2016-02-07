from django.core.exceptions import ValidationError
from django.db import models

from core.core import VOTE_TYPE_CHOICES, VoteTypes
from post.models import Candidate


class Vote(models.Model):
    candidate = models.ForeignKey(Candidate, related_name='votes')
    vote = models.SmallIntegerField(choices=VOTE_TYPE_CHOICES, default=VoteTypes.NEUTRAL)
    casted_at = models.DateTimeField(auto_now_add=True)

    def clean(self):
        if not self.yes and not self.no and not self.neutral:
            raise ValidationError('Yes, no, neutral can\'t be blank together')

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.clean()
        return super().save(force_insert=force_insert, force_update=force_update, using=using,
                            update_fields=update_fields)
