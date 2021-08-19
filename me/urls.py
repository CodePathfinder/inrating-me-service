from django.urls import path

from . import views

urlpatterns = [
    # API Route
    path("me", views.me_info, name="me"),
]
