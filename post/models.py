from django.db import models

from core.core import PostTypes, POST_TYPE_CHOICES
from election.models import Election


class Post(models.Model):
    name = models.CharField(max_length=32, db_index=True)
    number = models.IntegerField(default=1)
    election = models.ForeignKey(Election, related_name='posts', db_index=True)
    type = models.IntegerField(choices=POST_TYPE_CHOICES, default=0)
    order = models.PositiveSmallIntegerField(default=0)

    def __str__(self):
        type_string = ''
        if self.type == PostTypes.UG:
            type_string = ' [UG]'
        elif self.type == PostTypes.PG:
            type_string = ' [PG]'
        return self.name + type_string


class Candidate(models.Model):
    name = models.CharField(max_length=64, db_index=True)
    image = models.ImageField(null=True, blank=True)
    post = models.ForeignKey(Post, related_name='candidates', db_index=True)

    def __str__(self):
        return self.name
