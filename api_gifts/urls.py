from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    # API Route
    path("v1/gifts/available/", views.gifts, name="gifts"),
    path("v1/me", views.me_info, name="me"),
]
