from django.urls import path

from . import views

urlpatterns = [
    # API Routes
    path("get", views.UserDetails.as_view(), name="user_details"),
    path("me", views.MeDetails.as_view(), name="me"),
]
