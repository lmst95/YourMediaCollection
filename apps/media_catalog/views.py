"""
Views for media_catalog app (CRITICAL FILE #8).
"""

from rest_framework import generics, filters
from rest_framework.permissions import AllowAny, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter
from apps.media_catalog.models import Media, MediaType
from apps.media_catalog.serializers import MediaSerializer, MediaListSerializer
from .filters import MediaFilter


@extend_schema_view(
    get=extend_schema(
        summary="List all media",
        description="Get a paginated list of media items. Supports filtering by type, genre, and search.",
        tags=["Media"],
        parameters=[
            OpenApiParameter(
                name='media_type',
                description='Filter by media type (movie, tv_series, book, music, concert, document)',
                required=False,
                type=str
            ),
            OpenApiParameter(
                name='genre',
                description='Filter by genre',
                required=False,
                type=str
            ),
            OpenApiParameter(
                name='search',
                description='Search in title and description',
                required=False,
                type=str
            ),
        ]
    )
)
class MediaListView(generics.ListAPIView):
    """
    List all media with filtering and search.
    GET /api/media/
    """
    queryset = Media.objects.filter(is_public=True).order_by('-created_at')
    serializer_class = MediaListSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = MediaFilter
    search_fields = ['title', 'description']
    ordering_fields = ['title', 'release_date', 'created_at']
    ordering = ['-created_at']


@extend_schema_view(
    get=extend_schema(
        summary="Get media details",
        description="Retrieve detailed information about a specific media item.",
        tags=["Media"],
    )
)
class MediaDetailView(generics.RetrieveAPIView):
    """
    Get media details by ID.
    GET /api/media/{id}/
    """
    queryset = Media.objects.filter(is_public=True)
    serializer_class = MediaSerializer
    permission_classes = [AllowAny]


@extend_schema_view(
    post=extend_schema(
        summary="Create custom media",
        description="Create a custom media entry (concert or document). Requires authentication.",
        tags=["Media"],
    )
)
class MediaCreateView(generics.CreateAPIView):
    """
    Create custom media (concerts, documents).
    POST /api/media/
    """
    queryset = Media.objects.all()
    serializer_class = MediaSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        """Set created_by and is_public for user-created media."""
        serializer.save(
            created_by=self.request.user,
            is_public=False  # User-created media is private by default
        )


@extend_schema_view(
    get=extend_schema(
        summary="List movies",
        description="Get a list of movies with filtering and search.",
        tags=["Media - Movies"],
    )
)
class MovieListView(generics.ListAPIView):
    """
    List movies.
    GET /api/media/movies/
    """
    queryset = Media.objects.filter(media_type=MediaType.MOVIE, is_public=True).order_by('-release_date')
    serializer_class = MediaListSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = MediaFilter
    search_fields = ['title', 'description']
    ordering_fields = ['title', 'release_date', 'created_at']


@extend_schema_view(
    get=extend_schema(
        summary="List TV series",
        description="Get a list of TV series with filtering and search.",
        tags=["Media - TV Series"],
    )
)
class TVSeriesListView(generics.ListAPIView):
    """
    List TV series.
    GET /api/media/tv-series/
    """
    queryset = Media.objects.filter(media_type=MediaType.TV_SERIES, is_public=True).order_by('-release_date')
    serializer_class = MediaListSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = MediaFilter
    search_fields = ['title', 'description']
    ordering_fields = ['title', 'release_date', 'created_at']


@extend_schema_view(
    get=extend_schema(
        summary="List books",
        description="Get a list of books with filtering and search.",
        tags=["Media - Books"],
    )
)
class BookListView(generics.ListAPIView):
    """
    List books.
    GET /api/media/books/
    """
    queryset = Media.objects.filter(media_type=MediaType.BOOK, is_public=True).order_by('-release_date')
    serializer_class = MediaListSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = MediaFilter
    search_fields = ['title', 'description']
    ordering_fields = ['title', 'release_date', 'created_at']


@extend_schema_view(
    get=extend_schema(
        summary="List music albums",
        description="Get a list of music albums with filtering and search.",
        tags=["Media - Music"],
    )
)
class MusicListView(generics.ListAPIView):
    """
    List music albums.
    GET /api/media/music/
    """
    queryset = Media.objects.filter(media_type=MediaType.MUSIC, is_public=True).order_by('-release_date')
    serializer_class = MediaListSerializer
    permission_classes = [AllowAny]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = MediaFilter
    search_fields = ['title', 'description']
    ordering_fields = ['title', 'release_date', 'created_at']


@extend_schema_view(
    get=extend_schema(
        summary="Get available genres",
        description="Get a list of all unique genres across all media types.",
        tags=["Media"],
    )
)
class GenreListView(generics.GenericAPIView):
    """
    List all available genres.
    GET /api/media/genres/
    """
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        """Return unique genres from all media."""
        from django.db.models import Func, F
        from rest_framework.response import Response

        # Get all genres (they're stored as JSON arrays)
        media_with_genres = Media.objects.filter(is_public=True).exclude(genres=[])

        # Extract unique genres
        genres = set()
        for media in media_with_genres:
            if media.genres:
                genres.update(media.genres)

        return Response({
            'genres': sorted(list(genres))
        })
