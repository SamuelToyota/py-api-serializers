from django.db import models

class Genre(models.Model):
    name: str = models.CharField(max_length=100)

    def __str__(self) -> str:
        return self.name


class Movie(models.Model):
    title: str = models.CharField(max_length=255)
    description: str = models.TextField()
    release_year: int = models.IntegerField()
    genre: Genre = models.ForeignKey(Genre, on_delete=models.CASCADE, related_name='movies')
    actors: models.Manager = models.ManyToManyField("Actor", related_name='movies')

    def __str__(self) -> str:
        return self.title


class Actor(models.Model):
    name: str = models.CharField(max_length=150)
    birth_year: int = models.IntegerField()

    def __str__(self) -> str:
        return self.name
