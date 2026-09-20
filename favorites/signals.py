from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Favorite
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Favorite)
def favorite_created(sender, instance, created, **kwargs):
    print('Loaging Signals')
    if created:
        logger.info(
            f"Favorite Book added with {instance.title} having {instance.rating} and author is {instance.author}")
