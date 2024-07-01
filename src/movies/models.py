import uuid

from django.db import models
from django.utils.text import slugify


# Create your models here.
class Movie(models.Model):
    class MovieType(models.TextChoices):
        MOVIE = "movie"
        SERIES = "series"

    imdb_id = models.CharField(primary_key=True, unique=True)
    title = models.CharField(max_length=255)
    type = models.TextField(choices=MovieType)
    description = models.TextField()
    year = models.DateField()
    genre = models.TextField()
    director = models.TextField()
    writers = models.TextField()
    actors = models.TextField()
    country = models.TextField()
    poster = models.CharField(max_length=255)
    awards = models.TextField()
    imdb_score = models.CharField()
    rottentomato_score = models.CharField()
    metacritic_score = models.CharField()
    filmweb_score = models.CharField(null=True, blank=True)
    groups = models.ManyToManyField("Group", related_name="movies")
    imdb_url = models.TextField()
    rottentomato_url = models.TextField()
    metacritic_url = models.TextField()
    filmweb_url = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.title


class Group(models.Model):
    code = models.CharField(
        primary_key=True,
        max_length=10,
        unique=True,
        editable=False,
    )
    name = models.CharField(max_length=150)
    slug = models.SlugField(unique=True)
    members = models.ManyToManyField(
        "User", through="GroupMembership", related_name="groups"
    )

    def save(self, *args, **kwargs):
        if not self.pk:
            self.generate_unique_code()
        original_slug = slugify(self.name)
        self.slug = original_slug
        if Group.objects.filter(slug=self.slug).exists():
            self.slug = f"{original_slug}-{uuid.uuid4().hex[:2]}"
        super().save(*args, **kwargs)

    def generate_unique_code(self):
        while True:
            self.code = uuid.uuid4().hex[:10]
            if not Group.objects.filter(code=self.code).exists():
                break

    def __str__(self):
        member_names = ", ".join([member.nickname for member in self.members.all()])
        return f"{self.name} {self.slug}: {member_names} - {self.code}"


class User(models.Model):
    nickname = models.CharField(max_length=100)

    def __str__(self):
        return self.nickname


class GroupMembership(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.nickname} - {self.group.name}"


class GroupMovie(models.Model):
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    average_score = models.DecimalField(
        max_digits=3, decimal_places=1, null=True, blank=True
    )
    watched = models.BooleanField(default=False)
    added_by = models.CharField(max_length=100, null=True, blank=True)

    class Meta:
        unique_together = ("group", "movie")

    def __str__(self):
        return f"{self.group.name} - {self.movie.title} - {self.average_score}"


class UserScore(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    score = models.DecimalField(max_digits=3, decimal_places=1)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)

    class Meta:
        unique_together = ("user", "movie", "group")

    def __str__(self):
        return (
            f"{self.user.nickname} - {self.movie.title} - {self.group} - {self.score}"
        )
