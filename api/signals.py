from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Project, TimelineEvent


@receiver(post_save, sender=Project)
def create_timeline_event(sender, instance, created, **kwargs):
    if created:
        TimelineEvent.objects.create(
            project=instance,
            event_description=f"Project '{instance.title}' has been created.",
        )
    else:
        TimelineEvent.objects.create(
            project=instance,
            event_description=f"Project '{instance.title}' has been updated.",
        )
