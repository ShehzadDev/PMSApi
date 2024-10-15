from django.db import models
from django.contrib.auth.models import User
from django.conf import settings


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_picture = models.ImageField(upload_to="images/", null=True, blank=True)
    role = models.CharField(max_length=20, choices=settings.ROLE_CHOICES)
    contact_number = models.CharField(max_length=15)

    def __str__(self):
        return self.user.username


class Project(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    team_members = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name="projects"
    )

    def __str__(self):
        return self.title


class Task(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    status = models.CharField(max_length=20, choices=settings.STATUS_CHOICES)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)
    assignee = models.ForeignKey(
        Profile, on_delete=models.SET_NULL, null=True, blank=True
    )

    def __str__(self):
        return self.title


class Document(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    file = models.FileField(upload_to="documents/")
    version = models.CharField(max_length=20)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Comment(models.Model):
    text = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE)
    project = models.ForeignKey(Project, on_delete=models.CASCADE)

    def __str__(self):
        return f"Comment by {self.author.username} on {self.task.title}"


class TimelineEvent(TimeStampedModel):
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, related_name="timeline_events"
    )
    event_description = models.TextField()

    def __str__(self):
        return f"Event for {self.project.title}: {self.event_description[:50]}"


class Notification(TimeStampedModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notification for {self.user.username}: {self.message}"
