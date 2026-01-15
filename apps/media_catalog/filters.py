"""
Filters for media_catalog app.
"""

import django_filters
from apps.media_catalog.models import Media, MediaType


class MediaFilter(django_filters.FilterSet):
    """Filter for Media queryset."""

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

    title_contains = django_filters.CharFilter(
        field_name='title',
        lookup_expr='icontains',
        help_text='Filter by title (case-insensitive)'
    )

    class Meta:
        model = Media
        fields = ['media_type', 'genre', 'release_year', 'title_contains']

    def filter_genre(self, queryset, name, value):
        """
        Filter media by genre.
        Since genres is a JSONField containing a list, we need custom filtering.
        """
        return queryset.filter(genres__contains=[value])
