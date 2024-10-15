from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import (
    APIOverview,
    Register,
    Login,
    Logout,
    ProjectViewSet,
    TaskViewSet,
    DocumentViewSet,
    CommentViewSet,
    UserProfileView,
    TimelineEventListView,
    TimelineEventDetailView,
    NotificationListView,
    MarkNotificationReadView,
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)


router = DefaultRouter()
router.register(r"projects", ProjectViewSet, basename="projects")
router.register(r"tasks", TaskViewSet, basename="tasks")
router.register(r"documents", DocumentViewSet, basename="document")
router.register(r"comments", CommentViewSet, basename="comment")

urlpatterns = [
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/token/verify/", TokenVerifyView.as_view(), name="token_verify"),
    path("api/", APIOverview.as_view(), name="api-overview"),
    path("api/register/", Register.as_view(), name="register"),
    path("api/login/", Login.as_view(), name="login"),
    path("api/logout/", Logout.as_view(), name="logout"),
    path("api/profile/", UserProfileView.as_view(), name="user-profile"),
    path("api/timeline/", TimelineEventListView.as_view(), name="timeline-events-list"),
    path(
        "api/notifications/", NotificationListView.as_view(), name="notification-list"
    ),
    path(
        "api/notifications/<int:notification_id>/mark_read/",
        MarkNotificationReadView.as_view(),
        name="mark-notification-read",
    ),
    path(
        "api/timeline/<int:project_id>/",
        TimelineEventDetailView.as_view(),
        name="timeline-events-detail",
    ),
    path("api/", include(router.urls)),
]
