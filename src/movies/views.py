from datetime import datetime

from django.db.models import Avg
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from movies.utils.imdb import IMDbClient
from movies.utils.utils import get_metacritic_url, get_rotten_url

from .forms import (
    GroupForm,
    SetNicknameForm,
)
from .middleware import group_member_required
from .models import Group, GroupMovie, Movie, User, UserScore


def get_user_from_request(request):
    nickname = request.COOKIES.get("nickname")
    return get_object_or_404(User, nickname=nickname)


def set_nickname(request):
    if request.method == "POST":
        form = SetNicknameForm(request.POST)
        if form.is_valid():
            nickname = form.cleaned_data["nickname"]
            if User.objects.filter(nickname=nickname).exists():
                form.add_error("nickname", "This nickname is already taken.")
            else:
                User.objects.create(nickname=nickname)
                response = redirect("index")
                max_age = 365 * 24 * 60 * 60
                response.set_cookie("nickname", nickname, max_age=max_age)
                return response
    else:
        form = SetNicknameForm()

    return render(request, "set_nickname.html", {"nickname_form": form})


def index(request):
    user = get_user_from_request(request)
    groups = user.groups.all()
    return render(request, "index.html", {"groups": groups})


def create_group(request):
    if request.method == "POST":
        form = GroupForm(request.POST)
        if form.is_valid():
            group = form.save()
            user = get_user_from_request(request)
            group.members.add(user)
            return redirect("index")

    form = GroupForm()
    return redirect("index")


@group_member_required
def group_view(request, slug):
    user = get_user_from_request(request)
    group = get_object_or_404(Group, slug=slug)
    group_movies = GroupMovie.objects.filter(group=group)
    user_scores_queryset = UserScore.objects.filter(group=group).select_related("user")

    user_scores = {}
    for score in user_scores_queryset:
        movie_id = score.movie.imdb_id
        if movie_id not in user_scores:
            user_scores[movie_id] = []
        user_scores[movie_id].append((score.user.nickname, score.score))

    watched_movies = group_movies.filter(watched=True)
    not_watched_movies = group_movies.filter(watched=False)
    all_group_movies = watched_movies | not_watched_movies

    context = {
        "groups": user.groups.all(),
        "group": group,
        "user_scores": user_scores,
        "all_group_movies": all_group_movies,
        "watched_movies": watched_movies,
        "not_watched_movies": not_watched_movies,
    }
    return render(request, "group.html", context)


@require_POST
def join_group(request):
    code = request.POST.get("code")
    if code:
        group = get_object_or_404(Group, code=code)
        user = get_user_from_request(request)
        group.members.add(user)
        return redirect("group", slug=group.slug)
    return redirect("index")


@require_POST
def search_movies(request):
    query = request.POST.get("query")
    if query:
        movies = IMDbClient.fetch_search_query(query=query)
        return JsonResponse({"movies": movies})

    return JsonResponse({"error": "No query parameter provided."}, status=400)


@require_POST
def add_movie(request):
    user = get_user_from_request(request)
    movie_id = request.POST.get("movie_id")
    group_code = request.POST.get("group_code")

    if not movie_id or not group_code:
        return HttpResponseBadRequest("Missing parameters")

    group = get_object_or_404(Group, code=group_code)
    movie = Movie.objects.filter(imdb_id=movie_id).first()

    if not movie:
        movie_details = IMDbClient.fetch_movie_details(movie_id)
        if not movie_details:
            return HttpResponseBadRequest("Failed to fetch movie details from IMDb.")

        released_date = movie_details.get("Released")
        if released_date:
            released_date = datetime.strptime(released_date, "%d %b %Y").date()

        title = movie_details.get("Title")
        type = movie_details.get("Type")

        imdb_url = f"https://www.imdb.com/title/{movie_id}"
        rottentomato_url = get_rotten_url(title, type)
        metacritic_url = get_metacritic_url(title, type)

        movie = Movie.objects.create(
            imdb_id=movie_id,
            title=title,
            type=type,
            description=movie_details.get("Plot"),
            year=released_date,
            genre=movie_details.get("Genre"),
            director=movie_details.get("Director"),
            writers=movie_details.get("Writer"),
            actors=movie_details.get("Actors"),
            country=movie_details.get("Country"),
            poster=movie_details.get("Poster"),
            awards=movie_details.get("Awards"),
            imdb_score=movie_details.get("imdbRating", "N/A"),
            rottentomato_score=movie_details["Ratings"][1]["Value"]
            if len(movie_details.get("Ratings", [])) > 1
            else "N/A",
            metacritic_score=movie_details.get("Metascore", "N/A"),
            filmweb_score=None,
            imdb_url=imdb_url,
            rottentomato_url=rottentomato_url,
            metacritic_url=metacritic_url,
            filmweb_url=None,
        )

    GroupMovie.objects.get_or_create(group=group, movie=movie, added_by=user.nickname)

    return JsonResponse(
        {"msg": f"{movie.title} has been added to {group.name}"},
        status=200,
    )


@require_POST
def add_user_score(request):
    nickname = request.COOKIES.get("nickname")
    movie_id = request.POST.get("movie_id")
    group_code = request.POST.get("group_code")
    user_score = request.POST.get("score")

    if nickname and group_code and user_score and movie_id:
        user = get_object_or_404(User, nickname=nickname)
        group = get_object_or_404(Group, code=group_code)
        movie = get_object_or_404(Movie, imdb_id=movie_id)
        user_score = UserScore.objects.update_or_create(
            user=user,
            movie=movie,
            group=group,
            defaults={"score": user_score},
        )

        group_movie = get_object_or_404(GroupMovie, group=group, movie=movie)
        avg_score = UserScore.objects.filter(movie=movie, group=group).aggregate(
            Avg("score")
        )["score__avg"]
        group_movie.average_score = avg_score

        scores_count = UserScore.objects.filter(movie=movie, group=group).count()
        if scores_count >= 2 or scores_count == group.members.count():
            group_movie.watched = True

        group_movie.save()

        return redirect("group", slug=group.slug)

    return JsonResponse({"error": "Missing parameter to set score"}, status=400)
