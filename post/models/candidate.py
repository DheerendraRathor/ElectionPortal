from django.db import models

from .post import Post


def candidate_image_upload(candidate, filename):
    return '/'.join([candidate.post.election.name, candidate.post.name, filename])


class Candidate(models.Model):
    name = models.CharField(max_length=64, db_index=True)
    image = models.ImageField(upload_to=candidate_image_upload, max_length=512, null=True, blank=True)
    post = models.ForeignKey(Post, related_name='candidates', db_index=True)
    order = models.IntegerField(default=0, help_text='Sorting order of candidates')
    is_nota = models.BooleanField(default=False, editable=False)
    is_neutral = models.BooleanField(default=False, editable=False)
    auto_generated = models.BooleanField(default=False, editable=False)

    def __str__(self):
        return self.name
