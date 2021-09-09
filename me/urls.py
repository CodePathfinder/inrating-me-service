from django.urls import path

from . import views

urlpatterns = [
    # API Route
    path("me", views.get_user_data, name="me"),
    path("get", views.get_user_data, name="get_user_data"),
]
