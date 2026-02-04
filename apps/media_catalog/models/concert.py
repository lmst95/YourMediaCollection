"""
Concert model - user-created concert entries.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from .base import Media


class Concert(Media):
    """Concert-specific fields for user-created concert entries."""

    artist = models.CharField(_('artist'), max_length=200)
    venue = models.CharField(_('venue'), max_length=200, blank=True)
    location = models.CharField(
        _('location'),
        max_length=200,
        blank=True,
        help_text=_('City, Country')
    )
    event_date = models.DateField(_('event date'), null=True, blank=True)

    class Meta:
        db_table = 'media_catalog_concert'
        verbose_name = _('concert')
        verbose_name_plural = _('concerts')

    def __str__(self):
        return self.title
