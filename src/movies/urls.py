from django.urls import path

from . import views

urlpatterns = [
    path("search/", views.search_movies, name="search_movies"),
    path("add-movie/", views.add_movie, name="add_movie"),
]
