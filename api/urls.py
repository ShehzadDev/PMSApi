from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import APIOverview, Register, Login, Logout, ProjectViewSet

router = DefaultRouter()
router.register(r"projects", ProjectViewSet, basename="projects")

urlpatterns = [
    path("api/", APIOverview.as_view(), name="api-overview"),
    path("api/register/", Register.as_view(), name="register"),
    path("api/login/", Login.as_view(), name="login"),
    path("api/logout/", Logout.as_view(), name="logout"),
    path("api/", include(router.urls)),
]
