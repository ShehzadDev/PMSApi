from django.contrib import admin
from .models import (
    Profile,
    Project,
    Task,
    Document,
    Comment,
    TimelineEvent,
    Notification,
)

admin.site.register(Profile)
admin.site.register(Project)
admin.site.register(Task)
admin.site.register(Document)
admin.site.register(Comment)
admin.site.register(TimelineEvent)
admin.site.register(Notification)
