"""
Music model - specific fields for music albums/singles.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _
from .base import Media


class MusicAlbumType(models.TextChoices):
    """Music album type choices."""
    ALBUM = 'album', _('Album')
    SINGLE = 'single', _('Single')
    COMPILATION = 'compilation', _('Compilation')
    EP = 'ep', _('EP')


class Music(models.Model):
    """Music-specific fields extending the base Media model."""

    media_ptr = models.OneToOneField(
        Media,
        on_delete=models.CASCADE,
        parent_link=True,
        primary_key=True,
        related_name='music'
    )

    artists = models.JSONField(
        _('artists'),
        default=list,
        blank=True,
        help_text=_('List of artists')
    )
    album_type = models.CharField(
        _('album type'),
        max_length=20,
        choices=MusicAlbumType.choices,
        blank=True
    )
    track_count = models.PositiveIntegerField(
        _('track count'),
        null=True,
        blank=True
    )
    duration_seconds = models.PositiveIntegerField(
        _('duration (seconds)'),
        null=True,
        blank=True
    )
    label = models.CharField(_('record label'), max_length=200, blank=True)

    # External API ID
    musicbrainz_id = models.UUIDField(
        _('MusicBrainz ID'),
        unique=True,
        null=True,
        blank=True
    )

    class Meta:
        db_table = 'media_catalog_music'
        verbose_name = _('music')
        verbose_name_plural = _('music')

    def __str__(self):
        return self.media_ptr.title
