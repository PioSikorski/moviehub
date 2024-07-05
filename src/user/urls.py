from django.urls import path

from . import views

urlpatterns = [
    path("start/", views.start_view, name="start"),
    path("profile/", views.profile, name="profile"),
]
