# Generated by Django 5.0.6 on 2024-07-04 11:41

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Movie',
            fields=[
                ('imdb_id', models.CharField(max_length=255, primary_key=True, serialize=False, unique=True)),
                ('title', models.CharField(max_length=255)),
                ('type', models.CharField(choices=[('movie', 'Movie'), ('series', 'Series')], max_length=10)),
                ('description', models.TextField()),
                ('year', models.DateField()),
                ('genre', models.TextField()),
                ('director', models.TextField()),
                ('writers', models.TextField()),
                ('actors', models.TextField()),
                ('country', models.TextField()),
                ('poster', models.CharField(max_length=255)),
                ('awards', models.TextField()),
                ('imdb_score', models.CharField(max_length=10)),
                ('rottentomato_score', models.CharField(max_length=10)),
                ('metacritic_score', models.CharField(max_length=10)),
                ('filmweb_score', models.CharField(blank=True, max_length=10, null=True)),
                ('imdb_url', models.TextField()),
                ('rottentomato_url', models.TextField()),
                ('metacritic_url', models.TextField()),
                ('filmweb_url', models.TextField(blank=True, null=True)),
            ],
        ),
    ]
