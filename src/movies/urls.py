from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("set_nickname/", views.set_nickname, name="set_nickname"),
    path("create_group/", views.create_group, name="create_group"),
    path("join_group/", views.join_group, name="join_group"),
    path("group/<slug:slug>/", views.group_view, name="group"),
    path("search/", views.search_movies, name="search_movies"),
    path("add_movie/", views.add_movie, name="add_movie"),
    path("add_score/", views.add_user_score, name="add_user_score"),
]
