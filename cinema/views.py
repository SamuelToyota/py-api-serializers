from rest_framework import viewsets, status
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Actor, Genre, CinemaHall, Movie, MovieSession
from .serializers import (
    ActorSerializer,
    GenreSerializer,
    CinemaHallSerializer,
    MovieWriteSerializer,
    MovieListSerializer,
    MovieDetailSerializer,
    MovieSessionListSerializer,
    MovieSessionDetailSerializer,
)


# --------------------
# GenreViewSet (ModelViewSet)
# --------------------
class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


# --------------------
# ActorViewSet (ModelViewSet)
# --------------------
class ActorViewSet(viewsets.ModelViewSet):
    queryset = Actor.objects.all()
    serializer_class = ActorSerializer


# --------------------
# CinemaHallViewSet (ModelViewSet)
# --------------------
class CinemaHallViewSet(viewsets.ModelViewSet):
    queryset = CinemaHall.objects.all()
    serializer_class = CinemaHallSerializer


# --------------------
# MovieViewSet (ModelViewSet) - usa serializers diferentes para list / retrieve / create/update
# --------------------
class MovieViewSet(viewsets.ModelViewSet):
    queryset = Movie.objects.all()

    def get_serializer_class(self):
        # List -> compact view (genres names, actors full names)
        if self.action == "list":
            return MovieListSerializer
        # Retrieve -> detailed nested
        if self.action == "retrieve":
            return MovieDetailSerializer
        # create / update / partial_update -> use write serializer
        return MovieWriteSerializer

    # Garantir códigos HTTP explícitos em respostas (boa prática)
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        # retornar detail representation after create
        detail_serializer = MovieDetailSerializer(instance)
        return Response(detail_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        serializer = MovieWriteSerializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        detail_serializer = MovieDetailSerializer(instance)
        return Response(detail_serializer.data, status=status.HTTP_200_OK)

    def partial_update(self, request, *args, **kwargs):
        return self.update(request, partial=True, *args, **kwargs)


# --------------------
# MovieSessionViewSet (ModelViewSet) - serializers different for list / retrieve
# --------------------
class MovieSessionViewSet(viewsets.ModelViewSet):
    queryset = MovieSession.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return MovieSessionListSerializer
        if self.action == "retrieve":
            return MovieSessionDetailSerializer
        # for create/update use a simple serializer that accepts FK ids
        class _WriteSerializer(serializers.ModelSerializer):
            class Meta:
                model = MovieSession
                fields = ("id", "show_time", "movie", "cinema_hall")
        return _WriteSerializer

    def list(self, request, *args, **kwargs):
        qs = self.filter_queryset(self.get_queryset()).order_by("-show_time")
        serializer = self.get_serializer(qs, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        # use generated write serializer
        WriteSerializer = self.get_serializer_class()
        serializer = WriteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        detail_serializer = MovieSessionDetailSerializer(instance)
        return Response(detail_serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()
        WriteSerializer = self.get_serializer_class()
        serializer = WriteSerializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        detail_serializer = MovieSessionDetailSerializer(instance)
        return Response(detail_serializer.data, status=status.HTTP_200_OK)
