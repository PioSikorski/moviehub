from django.urls import path

from . import views

urlpatterns = [
    path("group/<slug:slug>", views.group_view, name="group"),
    path("join-group/", views.join_group, name="join_group"),
    path("create-group/", views.create_group, name="create_group"),
    path("add-score/", views.add_user_score, name="add_user_score"),
    path("group/<slug:slug>/info", views.group_info, name="group_info"),
    path("group-leave/", views.leave_group, name="leave_group"),
    path("join/<str:code>/", views.join_group_by_link, name="join_group_by_link"),
    path(
        "group/<slug:slug>/invite/",
        views.generate_invite_link,
        name="generate_invite_link",
    ),
]
