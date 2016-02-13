import os

from django.db.models.signals import post_save, pre_save, post_delete
from django.dispatch import receiver
from django.templatetags.static import static

from post.models import Post, Candidate


@receiver(post_save, sender=Post)
def create_default_candidates(sender, instance: Post, **kwargs) -> None:
    """
    Create default candidates like neutral and nota for a post if election permits

    Args:
        post: Post for which default candidates are required

    """
    try:
        Candidate.objects.get_or_create(is_nota=True, post=instance, defaults={
            'name': 'None of the Above',
            'image': static('img/nota.jpg'),
            'auto_generated': True,
        })
    except Candidate.MultipleObjectsReturned:
        pass

    try:
        Candidate.objects.get_or_create(is_neutral=True, post=instance, defaults={
            'name': 'Neutral',
            'image': static('img/neutral.png'),
            'auto_generated': True,
        })
    except Candidate.MultipleObjectsReturned:
        pass


@receiver(post_delete, sender=Candidate)
def auto_delete_file_on_delete(sender, instance: Candidate, **kwargs) -> None:
    """Deletes file from filesystem
    when corresponding `MediaFile` object is deleted.
    """
    if instance.auto_generated:
        return
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)


@receiver(pre_save, sender=Candidate)
def auto_delete_file_on_change(sender, instance: Candidate, **kwargs):
    """Deletes file from filesystem
    when corresponding `MediaFile` object is changed.
    """
    if not instance.pk:
        return False

    if instance.auto_generated:
        return False

    try:
        old_image = Candidate.objects.get(pk=instance.pk).image
    except Candidate.DoesNotExist:
        return False

    new_image = instance.image
    if not old_image == new_image:
        if os.path.isfile(old_image.path):
            os.remove(old_image.path)