from django.urls import path

from . import views

urlpatterns = [
    path("group/<slug:slug>", views.group_view, name="group"),
    path("join_group/", views.join_group, name="join_group"),
    path("create_group/", views.create_group, name="create_group"),
    path("add_score/", views.add_user_score, name="add_user_score"),
    path("group/<slug:slug>/info", views.group_info, name="group_info"),
    path("group_leave/", views.leave_group, name="leave_group"),
]
