from datetime import datetime
from unittest.mock import patch

from django.db.models import Avg
from django.test import Client, TestCase
from django.urls import reverse

from movies.models import Group, GroupMovie, Movie, User, UserScore


class SetNicknameTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_set_nickname(self):
        response = self.client.post(reverse("set_nickname"), {"nickname": "newuser"})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(nickname="newuser").exists())
        self.assertRedirects(response, reverse("index"))

    def test_set_nickname_nickname_taken(self):
        response = self.client.post(reverse("set_nickname"), {"nickname": "newuser"})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(nickname="newuser").exists())

        client = Client()
        response_taken = client.post(reverse("set_nickname"), {"nickname": "newuser"})
        self.assertEqual(response_taken.status_code, 200)
        self.assertContains(response_taken, "This nickname is already taken.")


class IndexTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(nickname="testuser")
        self.client.cookies["nickname"] = self.user.nickname

    def test_index(self):
        response = self.client.get(reverse("index"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")

    def test_index_without_nickname(self):
        client = Client()
        response = client.get(reverse("index"))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("set_nickname"))

    def test_create_group(self):
        response = self.client.post(reverse("create_group"), {"name": "New Group"})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Group.objects.filter(name="New Group").exists())
        self.assertRedirects(response, reverse("index"))

    def test_create_group_with_same_name(self):
        client = Client()
        user = User.objects.create(nickname="newuser")
        client.cookies["nickname"] = user.nickname

        response = self.client.post(reverse("create_group"), {"name": "New Group"})
        response = client.post(reverse("create_group"), {"name": "New Group"})
        self.assertTrue(Group.objects.filter(name="New Group").count() == 2)
        self.assertRedirects(response, reverse("index"))

    @patch("movies.views.IMDbClient.fetch_search_query")
    def test_search_movies_with_query(self, mock_fetch_search_query):
        mock_fetch_search_query.return_value = [
            {"title": "John Paul II", "year": 2137, "imdb_id": "tt213769420"}
        ]
        response = self.client.post(reverse("search_movies"), {"query": "john paul"})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "movies": [
                    {
                        "title": "John Paul II",
                        "year": 2137,
                        "imdb_id": "tt213769420",
                    }
                ]
            },
        )
        mock_fetch_search_query.assert_called_once_with(query="john paul")

    @patch("movies.views.IMDbClient.fetch_search_query")
    def test_search_movies_without_query(self, mock_fetch_search_query):
        response = self.client.post(reverse("search_movies"), {"query": ""})

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "No query parameter provided."})
        mock_fetch_search_query.assert_not_called()


class GroupViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(nickname="testuser")
        self.group = Group.objects.create(name="Test Group")
        self.group.members.add(self.user)
        self.client.cookies["nickname"] = self.user.nickname

    def test_group_view(self):
        response = self.client.get(reverse("group", args=[self.group.slug]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "group.html")

    def test_group_view_without_being_member(self):
        client = Client()
        self.user = User.objects.create(nickname="newuser")
        self.client.cookies["nickname"] = self.user.nickname

        response = client.get(reverse("group", args=[self.group.slug]))
        self.assertEqual(response.status_code, 302)


class JoinGroupTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(nickname="testuser")
        self.group = Group.objects.create(name="Test Group")
        self.client.cookies["nickname"] = self.user.nickname

    def test_join_group(self):
        response = self.client.post(reverse("join_group"), {"code": self.group.code})
        self.assertEqual(response.status_code, 302)
        self.assertIn(self.user, self.group.members.all())
        self.assertRedirects(response, reverse("group", args=[self.group.slug]))

    def test_join_group_wrong_code(self):
        response = self.client.post(reverse("join_group"), {"code": "21374206"})
        self.assertEqual(response.status_code, 404)
        self.assertNotIn(self.user, self.group.members.all())


class MovieDetailsTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create(nickname="testuser")
        self.group = Group.objects.create(name="Test Group")
        self.group.members.add(self.user)
        self.client.cookies["nickname"] = self.user.nickname
        self.movie_details = {
            "Title": "The Shawshank Redemption",
            "Type": "movie",
            "Plot": "Two imprisoned men bond over a number of years, finding solace and eventual redemption through acts of common decency.",
            "Released": "14 Oct 1994",
            "Genre": "Drama",
            "Director": "Frank Darabont",
            "Writer": 'Stephen King (short story "Rita Hayworth and Shawshank Redemption"), Frank Darabont (screenplay)',
            "Actors": "Tim Robbins, Morgan Freeman, Bob Gunton",
            "Country": "USA",
            "Poster": "https://example.com/poster.jpg",
            "Awards": "Nominated for 7 Oscars. Another 21 wins & 36 nominations.",
            "imdbRating": "9.3",
            "Ratings": [
                {"Source": "Internet Movie Database", "Value": "9.3/10"},
                {"Source": "Rotten Tomatoes", "Value": "91%"},
                {"Source": "Metacritic", "Value": "80/100"},
            ],
            "Metascore": "80",
        }
        movie_id = "tt0111161"
        self.movie = Movie.objects.create(
            imdb_id=movie_id,
            type=self.movie_details["Type"],
            title=self.movie_details["Title"],
            description=self.movie_details["Plot"],
            year=datetime.strptime(self.movie_details["Released"], "%d %b %Y").date(),
            genre=self.movie_details["Genre"],
            director=self.movie_details["Director"],
            writers=self.movie_details["Writer"],
            actors=self.movie_details["Actors"],
            country=self.movie_details["Country"],
            poster=self.movie_details["Poster"],
            awards=self.movie_details["Awards"],
            imdb_score=self.movie_details["imdbRating"],
            rottentomato_score=self.movie_details["Ratings"][1]["Value"]
            if len(self.movie_details.get("Ratings", [])) > 1
            else "N/A",
            metacritic_score=self.movie_details["Metascore"],
            filmweb_score=None,
            filmweb_url=None,
        )

    def test_add_movie_missing_parameters(self):
        response = self.client.post(
            reverse("add_movie"), {"movie_id": "", "group_code": ""}
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.content.decode(), "Missing parameters")

    def test_add_existing_movie(self):
        response = self.client.post(
            reverse("add_movie"),
            {"movie_id": self.movie.imdb_id, "group_code": self.group.code},
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(
            GroupMovie.objects.filter(group=self.group, movie=self.movie).exists()
        )
        self.assertEqual(
            response.json(),
            {"msg": f"{self.movie.title} has been added to {self.group.name}"},
        )

    @patch("movies.views.IMDbClient.fetch_movie_details")
    def test_add_new_movie(self, mock_fetch_movie_details):
        mock_fetch_movie_details.return_value = {
            "Title": "Inception",
            "Type": "movie",
            "Plot": "A thief who steals corporate secrets...",
            "Released": "16 Jul 2010",
            "Genre": "Action, Adventure, Sci-Fi",
            "Director": "Christopher Nolan",
            "Writer": "Christopher Nolan",
            "Actors": "Leonardo DiCaprio, Joseph Gordon-Levitt, Ellen Page",
            "Country": "USA, UK",
            "Poster": "https://example.com/poster.jpg",
            "Awards": "Won 4 Oscars. Another 152 wins & 204 nominations.",
            "imdbRating": "8.8",
            "Ratings": [
                {"Source": "Internet Movie Database", "Value": "8.8/10"},
                {"Source": "Rotten Tomatoes", "Value": "87%"},
            ],
            "Metascore": "74",
        }
        response = self.client.post(
            reverse("add_movie"),
            {"movie_id": "tt1375666", "group_code": self.group.code},
        )
        self.assertEqual(response.status_code, 200)
        new_movie = Movie.objects.get(imdb_id="tt1375666")
        self.assertTrue(
            GroupMovie.objects.filter(group=self.group, movie=new_movie).exists()
        )
        self.assertEqual(
            response.json(),
            {"msg": f"{new_movie.title} has been added to {self.group.name}"},
        )
        mock_fetch_movie_details.assert_called_once_with("tt1375666")

    @patch("movies.views.IMDbClient.fetch_movie_details")
    def test_add_user_score_missing_parameters(self, mock_fetch_movie_details):
        mock_fetch_movie_details.return_value = self.movie_details

        response = self.client.post(
            reverse("add_user_score"), {"movie_id": "", "group_code": "", "score": ""}
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"error": "Missing parameter to set score"})

    @patch("movies.views.IMDbClient.fetch_movie_details")
    def test_add_user_score_invalid_movie_id(self, mock_fetch_movie_details):
        mock_fetch_movie_details.return_value = self.movie_details

        response = self.client.post(
            reverse("add_user_score"),
            {"movie_id": "invalid_id", "group_code": self.group.code, "score": 8},
        )
        self.assertEqual(response.status_code, 404)

    def test_add_user_score_already_scored(self):
        GroupMovie.objects.create(group=self.group, movie=self.movie)
        UserScore.objects.create(
            user=self.user, movie=self.movie, group=self.group, score=8.5
        )

        response = self.client.post(
            reverse("add_user_score"),
            {"movie_id": "tt0111161", "group_code": self.group.code, "score": 7.5},
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("group", args=[self.group.slug]))

        user_score = UserScore.objects.get(
            user=self.user, movie=self.movie, group=self.group
        )
        self.assertEqual(user_score.score, 7.5)

    def test_add_user_score_update_average_and_watched(self):
        client = Client()
        GroupMovie.objects.create(group=self.group, movie=self.movie)
        UserScore.objects.create(
            user=self.user, movie=self.movie, group=self.group, score=6.5
        )
        other_user = User.objects.create(nickname="otheruser")
        self.group.members.add(other_user)
        client.cookies["nickname"] = other_user.nickname

        response = client.post(
            reverse("add_user_score"),
            {"movie_id": "tt0111161", "group_code": self.group.code, "score": 9.5},
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("group", args=[self.group.slug]))

        user_score = UserScore.objects.get(
            user=other_user, movie=self.movie, group=self.group
        )
        self.assertEqual(user_score.score, 9.5)

        group_movie = GroupMovie.objects.get(group=self.group, movie=self.movie)
        avg_score = UserScore.objects.filter(
            movie=self.movie, group=self.group
        ).aggregate(Avg("score"))["score__avg"]
        self.assertEqual(group_movie.average_score, avg_score)
        self.assertTrue(group_movie.watched)
