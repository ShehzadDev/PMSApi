from django.urls import path
from .views import (
    APIOverview,
    Register,
    Login,
    Logout,
    ProjectCreateView,
    ProjectListView,
    ProjectDetailView,
    ProjectUpdateView,
    ProjectDeleteView,
)

urlpatterns = [
    path("api/", APIOverview.as_view(), name="api-overview"),
    path("api/register/", Register.as_view(), name="register"),
    path("api/login/", Login.as_view(), name="login"),
    path("api/logout/", Logout.as_view(), name="logout"),
    path("api/projects/create", ProjectCreateView.as_view(), name="project-create"),
    path("api/projects/", ProjectListView.as_view(), name="project-list"),
    path("api/projects/<int:pk>/", ProjectDetailView.as_view(), name="project-detail"),
    path("api/projects/<int:pk>/", ProjectUpdateView.as_view(), name="project-update"),
    path("api/projects/<int:pk>/", ProjectDeleteView.as_view(), name="project-delete"),
]
