"""
TV Series model - specific fields for TV shows.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from .base import Media


class TVSeriesStatus(models.TextChoices):
    """TV Series status choices."""
    ONGOING = 'ongoing', _('Ongoing')
    ENDED = 'ended', _('Ended')
    CANCELLED = 'cancelled', _('Cancelled')


class TVSeries(Media):
    """TV Series-specific fields extending the base Media model."""

    number_of_seasons = models.PositiveIntegerField(
        _('number of seasons'),
        null=True,
        blank=True
    )
    number_of_episodes = models.PositiveIntegerField(
        _('number of episodes'),
        null=True,
        blank=True
    )
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=TVSeriesStatus.choices,
        blank=True
    )
    creators = models.JSONField(
        _('creators'),
        default=list,
        blank=True,
        help_text=_('List of series creators')
    )

    # External API ID
    tmdb_id = models.IntegerField(_('TMDb ID'), unique=True, null=True, blank=True)

    class Meta:
        db_table = 'media_catalog_tvseries'
        verbose_name = _('TV series')
        verbose_name_plural = _('TV series')

    def __str__(self):
        return self.title
