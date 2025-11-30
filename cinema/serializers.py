from rest_framework import serializers
from .models import Actor, Genre, CinemaHall, Movie, MovieSession


# --------------------
# Actor
# --------------------
class ActorSerializer(serializers.ModelSerializer):
    full_name = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Actor
        fields = ("id", "first_name", "last_name", "full_name")

    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"


# --------------------
# Genre
# --------------------
class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ("id", "name")


# --------------------
# CinemaHall
# --------------------
class CinemaHallSerializer(serializers.ModelSerializer):
    capacity = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = CinemaHall
        fields = ("id", "name", "rows", "seats_in_row", "capacity")

    def get_capacity(self, obj):
        return obj.capacity


# --------------------
# Movie (write serializer -> use PKs for M2M)
# --------------------
class MovieWriteSerializer(serializers.ModelSerializer):
    actors = serializers.PrimaryKeyRelatedField(many=True, queryset=Actor.objects.all())
    genres = serializers.PrimaryKeyRelatedField(many=True, queryset=Genre.objects.all())

    class Meta:
        model = Movie
        fields = ("id", "title", "description", "duration", "actors", "genres")


# --------------------
# Movie (list serializer -> genres as names, actors as full names)
# --------------------
class MovieListSerializer(serializers.ModelSerializer):
    genres = serializers.SerializerMethodField()
    actors = serializers.SerializerMethodField()

    class Meta:
        model = Movie
        fields = ("id", "title", "description", "duration", "genres", "actors")

    def get_genres(self, obj):
        return [g.name for g in obj.genres.all()]

    def get_actors(self, obj):
        return [f"{a.first_name} {a.last_name}" for a in obj.actors.all()]


# --------------------
# Movie (detail serializer -> full nested genres and actors)
# --------------------
class MovieDetailSerializer(serializers.ModelSerializer):
    genres = GenreSerializer(many=True, read_only=True)
    actors = ActorSerializer(many=True, read_only=True)

    class Meta:
        model = Movie
        fields = ("id", "title", "description", "duration", "genres", "actors")


# --------------------
# MovieSession (list serializer -> flattened fields)
# --------------------
class MovieSessionListSerializer(serializers.ModelSerializer):
    movie_title = serializers.CharField(source="movie.title", read_only=True)
    cinema_hall_name = serializers.CharField(source="cinema_hall.name", read_only=True)
    cinema_hall_capacity = serializers.SerializerMethodField()

    class Meta:
        model = MovieSession
        fields = ("id", "show_time", "movie_title", "cinema_hall_name", "cinema_hall_capacity")

    def get_cinema_hall_capacity(self, obj):
        return obj.cinema_hall.capacity


# --------------------
# MovieSession (detail serializer -> nested movie + nested cinema_hall)
# Movie nested should use MovieListSerializer (genres as names, actors as full names)
# CinemaHall nested uses CinemaHallSerializer (includes capacity)
# --------------------
class MovieSessionDetailSerializer(serializers.ModelSerializer):
    movie = MovieListSerializer(read_only=True)
    cinema_hall = CinemaHallSerializer(read_only=True)

    class Meta:
        model = MovieSession
        fields = ("id", "show_time", "movie", "cinema_hall")
