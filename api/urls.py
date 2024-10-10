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
)

router = DefaultRouter()
router.register(r"projects", ProjectViewSet, basename="projects")
router.register(r"tasks", TaskViewSet, basename="tasks")
router.register(r"documents", DocumentViewSet, basename="document")
router.register(r"comments", CommentViewSet, basename="comment")

urlpatterns = [
    path("api/", APIOverview.as_view(), name="api-overview"),
    path("api/register/", Register.as_view(), name="register"),
    path("api/login/", Login.as_view(), name="login"),
    path("api/logout/", Logout.as_view(), name="logout"),
    path("api/profile/", UserProfileView.as_view(), name="user-profile"),
    path("api/timeline/", TimelineEventListView.as_view(), name="timeline-events-list"),
    path(
        "api/timeline/<int:project_id>/",
        TimelineEventDetailView.as_view(),
        name="timeline-events-detail",
    ),
    path("api/", include(router.urls)),
]
