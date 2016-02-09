import os

from django.db import models
from django.dispatch import receiver

from .post import Post


def candidate_image_upload(candidate, filename):
    return '/'.join([candidate.post.election.name, candidate.post.name, filename])


class Candidate(models.Model):
    name = models.CharField(max_length=64, db_index=True)
    image = models.ImageField(upload_to=candidate_image_upload, null=True, blank=True)
    post = models.ForeignKey(Post, related_name='candidates', db_index=True)

    def __str__(self):
        return self.name


# These two auto-delete files from filesystem when they are unneeded:

@receiver(models.signals.post_delete, sender=Candidate)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """Deletes file from filesystem
    when corresponding `MediaFile` object is deleted.
    """
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)


@receiver(models.signals.pre_save, sender=Candidate)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """Deletes file from filesystem
    when corresponding `MediaFile` object is changed.
    """
    if not instance.pk:
        return False

    try:
        old_file = Candidate.objects.get(pk=instance.pk).file
    except Candidate.DoesNotExist:
        return False

    new_file = instance.file
    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)
