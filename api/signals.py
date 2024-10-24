from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import (
    Project,
    Task,
    Document,
    Comment,
    Profile,
    TimelineEvent,
    Notification,
)


@receiver(post_save, sender=Project)
def create_project_timeline_event(sender, instance, created, **kwargs):
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


@receiver(post_save, sender=Project)
def create_project_notification(sender, instance, created, **kwargs):
    if created:
        Notification.objects.create(
            user=instance.created_by,
            message=f"New project created: {instance.title}",
        )
        for member in instance.team_members.all():
            Notification.objects.create(
                user=member,
                message=f"You have been added to the project: {instance.title}",
            )


@receiver(post_save, sender=Task)
def create_task_timeline_event(sender, instance, created, **kwargs):
    if created:
        TimelineEvent.objects.create(
            project=instance.project,
            event_description=f"Task '{instance.title}' has been created.",
        )
    else:
        TimelineEvent.objects.create(
            project=instance.project,
            event_description=f"Task '{instance.title}' has been updated.",
        )


@receiver(post_save, sender=Task)
def create_task_notification(sender, instance, created, **kwargs):
    if created:
        if instance.assignee:
            Notification.objects.create(
                user=instance.assignee.user,
                message=f"You have been assigned a new task: {instance.title}",
            )


@receiver(post_save, sender=Document)
def create_document_timeline_event(sender, instance, created, **kwargs):
    if created:
        TimelineEvent.objects.create(
            project=instance.project,
            event_description=f"Document '{instance.name}' has been uploaded.",
        )
    else:
        TimelineEvent.objects.create(
            project=instance.project,
            event_description=f"Document '{instance.name}' has been updated.",
        )


@receiver(post_save, sender=Document)
def create_document_notification(sender, instance, created, **kwargs):
    for member in instance.project.team_members.all():
        Notification.objects.create(
            user=member,
            message=f"A document has been {'uploaded' if created else 'updated'}: {instance.name}",
        )


@receiver(post_save, sender=Comment)
def create_comment_timeline_event(sender, instance, created, **kwargs):
    TimelineEvent.objects.create(
        project=instance.task.project,
        event_description=f"Comment '{instance.text}' has been {'added' if created else 'updated'}.",
    )


@receiver(post_save, sender=Comment)
def create_comment_notification(sender, instance, created, **kwargs):
    user = instance.task.assignee.user

    Notification.objects.create(
        user=user,
        message=f"A comment has been {'added to' if created else 'updated in'} your task: {instance.task.title}",
    )


@receiver(post_save, sender=Profile)
def create_profile_notification(sender, instance, created, **kwargs):
    Notification.objects.create(
        user=instance.user,
        message=f"Your profile has been {'created' if created else 'updated'}.",
    )
