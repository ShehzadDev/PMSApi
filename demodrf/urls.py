"""
URL configuration for demodrf project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
"""

from django.contrib import admin
from django.urls import path, include
from api.views import api_overview, register, login, logout

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", api_overview, name="api-overview"),
    path("api/register/", register, name="register"),
    path("api/login/", login, name="login"),
    path("api/logout/", logout, name="logout"),
]
