"""
Movie model - specific fields for movies.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from .base import Media


class Movie(Media):
    """Movie-specific fields extending the base Media model."""

    runtime_minutes = models.PositiveIntegerField(
        _('runtime (minutes)'),
        null=True,
        blank=True
    )
    director = models.CharField(_('director'), max_length=200, blank=True)
    cast = models.JSONField(
        _('cast'),
        default=list,
        blank=True,
        help_text=_('List of main cast members')
    )

    # External API IDs
    tmdb_id = models.IntegerField(_('TMDb ID'), unique=True, null=True, blank=True)
    imdb_id = models.CharField(_('IMDb ID'), max_length=20, unique=True, blank=True)

    class Meta:
        db_table = 'media_catalog_movie'
        verbose_name = _('movie')
        verbose_name_plural = _('movies')

    def __str__(self):
        return self.title
