from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    APIOverview,
    Register,
    UserProfileView,
    TimelineEventView,
    ProjectViewSet,
    TaskViewSet,
    DocumentViewSet,
    CommentViewSet,
    NotificationViewSet,
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
router.register(r"notifications", NotificationViewSet, basename="notifications")

urlpatterns = [
    path("api/", APIOverview.as_view(), name="api-overview"),
    path("api/register/", Register.as_view(), name="register"),
    path("api/login/", TokenObtainPairView.as_view(), name="login"),
    path("api/profile/", UserProfileView.as_view(), name="user-profile"),
    path(
        "api/timeline/",
        TimelineEventView.as_view(),
        name="timeline-events-list",
    ),
    path(
        "api/timeline/<int:project_id>/",
        TimelineEventView.as_view(),
        name="timeline-events-detail",
    ),
    path("api/", include(router.urls)),
]
