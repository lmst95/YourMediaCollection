"""
Filters for media_catalog app.
"""

import django_filters
from django.db.models import Q
from apps.media_catalog.models import Media, MediaType


class MediaFilter(django_filters.FilterSet):
    """Advanced filter for Media queryset with support for creators/contributors."""

    media_type = django_filters.ChoiceFilter(
        field_name='media_type',
        choices=MediaType.choices,
        help_text='Filter by media type'
    )

    genre = django_filters.CharFilter(
        method='filter_genre',
        help_text='Filter by genre (partial match)'
    )

    release_year = django_filters.NumberFilter(
        field_name='release_date',
        lookup_expr='year',
        help_text='Filter by release year'
    )

    release_year_min = django_filters.NumberFilter(
        field_name='release_date',
        lookup_expr='year__gte',
        help_text='Filter by minimum release year'
    )

    release_year_max = django_filters.NumberFilter(
        field_name='release_date',
        lookup_expr='year__lte',
        help_text='Filter by maximum release year'
    )

    title_contains = django_filters.CharFilter(
        field_name='title',
        lookup_expr='icontains',
        help_text='Filter by title (case-insensitive)'
    )

    # Creator/contributor filters (work across different media types)
    author = django_filters.CharFilter(
        method='filter_author',
        help_text='Filter books by author name (case-insensitive)'
    )

    artist = django_filters.CharFilter(
        method='filter_artist',
        help_text='Filter music by artist name (case-insensitive)'
    )

    director = django_filters.CharFilter(
        method='filter_director',
        help_text='Filter movies by director name (case-insensitive)'
    )

    actor = django_filters.CharFilter(
        method='filter_actor',
        help_text='Filter movies/TV by actor/cast name (case-insensitive)'
    )

    creator = django_filters.CharFilter(
        method='filter_creator',
        help_text='Filter TV series by creator name (case-insensitive)'
    )

    # Generic creator filter that searches across all creator types
    contributor = django_filters.CharFilter(
        method='filter_contributor',
        help_text='Search across all creators (author, artist, director, actor, creator)'
    )

    class Meta:
        model = Media
        fields = [
            'media_type', 'genre', 'release_year', 'release_year_min', 'release_year_max',
            'title_contains', 'author', 'artist', 'director', 'actor', 'creator', 'contributor'
        ]

    def filter_genre(self, queryset, name, value):
        """Filter media by genre (case-insensitive partial match)."""
        # Use icontains-like behavior for JSON arrays
        return queryset.filter(
            Q(genres__icontains=value)
        )

    def filter_author(self, queryset, name, value):
        """Filter books by author name."""
        # Authors are stored in Book model as JSON field
        return queryset.filter(
            media_type=MediaType.BOOK,
            book__authors__icontains=value
        )

    def filter_artist(self, queryset, name, value):
        """Filter music by artist name."""
        # Artists are stored in Music model as JSON field
        return queryset.filter(
            media_type=MediaType.MUSIC,
            music__artists__icontains=value
        )

    def filter_director(self, queryset, name, value):
        """Filter movies by director name."""
        # Director is stored in Movie model as CharField
        return queryset.filter(
            media_type=MediaType.MOVIE,
            movie__director__icontains=value
        )

    def filter_actor(self, queryset, name, value):
        """Filter movies/TV by actor/cast name."""
        # Cast is stored in metadata for TV, and in Movie.cast for movies
        return queryset.filter(
            Q(media_type=MediaType.MOVIE, movie__cast__icontains=value) |
            Q(media_type=MediaType.TV_SERIES, metadata__cast__icontains=value)
        )

    def filter_creator(self, queryset, name, value):
        """Filter TV series by creator name."""
        # Creators are stored in TVSeries model as JSON field
        return queryset.filter(
            media_type=MediaType.TV_SERIES,
            tvseries__creators__icontains=value
        )

    def filter_contributor(self, queryset, name, value):
        """Search across all creator/contributor types."""
        return queryset.filter(
            Q(media_type=MediaType.BOOK, book__authors__icontains=value) |
            Q(media_type=MediaType.MUSIC, music__artists__icontains=value) |
            Q(media_type=MediaType.MOVIE, movie__director__icontains=value) |
            Q(media_type=MediaType.MOVIE, movie__cast__icontains=value) |
            Q(media_type=MediaType.TV_SERIES, tvseries__creators__icontains=value) |
            Q(media_type=MediaType.TV_SERIES, metadata__cast__icontains=value)
        )
