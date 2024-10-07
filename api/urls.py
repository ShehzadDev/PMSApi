from django.urls import path
from api.views import register, login, logout, api_overview

urlpatterns = [
    path("api/", api_overview, name="api-overview"),
    path("api/register/", register, name="register"),
    path("api/login/", login, name="login"),
    path("api/logout/", logout, name="logout"),
]
