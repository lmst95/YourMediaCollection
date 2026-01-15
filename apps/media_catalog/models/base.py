"""
Base Media model - the foundation for all media types.
This is CRITICAL FILE #2 from the architecture plan.
"""

import uuid
from django.db import models
from django.contrib.postgres.search import SearchVectorField
from django.contrib.postgres.indexes import GinIndex
from django.utils.translation import gettext_lazy as _
from django.conf import settings


class MediaType(models.TextChoices):
    """Media type enumeration."""
    MOVIE = 'movie', _('Movie')
    TV_SERIES = 'tv_series', _('TV Series')
    BOOK = 'book', _('Book')
    MUSIC = 'music', _('Music')
    CONCERT = 'concert', _('Concert')
    DOCUMENT = 'document', _('Document')


class Media(models.Model):
    """
    Base media model using polymorphic inheritance pattern.
    All media types (Movie, Book, Music, etc.) inherit from this model.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    media_type = models.CharField(
        _('media type'),
        max_length=20,
        choices=MediaType.choices,
        db_index=True
    )
    title = models.CharField(_('title'), max_length=500, db_index=True)
    description = models.TextField(_('description'), blank=True)
    release_date = models.DateField(_('release date'), null=True, blank=True)
    cover_image_url = models.URLField(_('cover image URL'), max_length=500, blank=True)

    # JSON fields for flexible data storage
    genres = models.JSONField(_('genres'), default=list, blank=True)
    external_ids = models.JSONField(
        _('external IDs'),
        default=dict,
        blank=True,
        help_text=_('External API IDs (tmdb_id, imdb_id, isbn, etc.)')
    )
    metadata = models.JSONField(
        _('metadata'),
        default=dict,
        blank=True,
        help_text=_('Type-specific metadata')
    )

    # User-created content flags
    is_public = models.BooleanField(
        _('is public'),
        default=True,
        help_text=_('False for user-created private entries')
    )
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_media',
        verbose_name=_('created by')
    )

    # Timestamps
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    # Full-text search vector
    search_vector = SearchVectorField(null=True, blank=True)

    class Meta:
        db_table = 'media_catalog_media'
        verbose_name = _('media')
        verbose_name_plural = _('media')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['media_type']),
            models.Index(fields=['title']),
            models.Index(fields=['release_date']),
            models.Index(fields=['is_public']),
            GinIndex(fields=['search_vector']),
            GinIndex(fields=['external_ids']),
            GinIndex(fields=['genres']),
        ]

    def __str__(self):
        return f"{self.get_media_type_display()}: {self.title}"

    def save(self, *args, **kwargs):
        """Override save to handle media type-specific logic."""
        super().save(*args, **kwargs)
        # Trigger Neo4j sync (will be implemented via signals)

    def get_specific(self):
        """
        Get the type-specific model instance (Movie, Book, etc.).
        Returns the child model if it exists, otherwise returns self.
        """
        type_map = {
            MediaType.MOVIE: 'movie',
            MediaType.TV_SERIES: 'tvseries',
            MediaType.BOOK: 'book',
            MediaType.MUSIC: 'music',
            MediaType.CONCERT: 'concert',
            MediaType.DOCUMENT: 'document',
        }

        related_name = type_map.get(self.media_type)
        if related_name and hasattr(self, related_name):
            return getattr(self, related_name)
        return self
