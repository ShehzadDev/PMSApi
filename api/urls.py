from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import (
    APIOverview,
    Register,
    UserProfileView,
    TimelineEventListView,
    TimelineEventDetailView,
    NotificationListView,
    MarkNotificationReadView,
    ProjectViewSet,
    TaskViewSet,
    DocumentViewSet,
    CommentViewSet,
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)

router = DefaultRouter()
router.register(r"projects", ProjectViewSet, basename="projects")
router.register(r"tasks", TaskViewSet, basename="tasks")
router.register(r"documents", DocumentViewSet, basename="documents")
router.register(r"comments", CommentViewSet, basename="comments")

urlpatterns = [
    path("api/", APIOverview.as_view(), name="api-overview"),
    path("api/register/", Register.as_view(), name="register"),
    path("api/login/", TokenObtainPairView.as_view(), name="login"),
    # path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # path("api/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("api/profile/", UserProfileView.as_view(), name="user-profile"),
    path("api/timeline/", TimelineEventListView.as_view(), name="timeline-events-list"),
    path(
        "api/timeline/<int:project_id>/",
        TimelineEventDetailView.as_view(),
        name="timeline-events-detail",
    ),
    path(
        "api/notifications/", NotificationListView.as_view(), name="notification-list"
    ),
    path(
        "api/notifications/<int:notification_id>/mark_read/",
        MarkNotificationReadView.as_view(),
        name="mark-notification-read",
    ),
    path("api/", include(router.urls)),
]
