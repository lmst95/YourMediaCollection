"""
Collections models - UserMedia linking users to their media collections.
This is CRITICAL FILE #3 from the architecture plan.
"""

import uuid
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from apps.media_catalog.models import Media


class CollectionStatus(models.TextChoices):
    """Status choices for user media collection items."""
    OWNED = 'owned', _('Owned')
    WATCHED = 'watched', _('Watched')
    READ = 'read', _('Read')
    LISTENED = 'listened', _('Listened')
    WISHLIST = 'wishlist', _('Wishlist')
    BORROWED = 'borrowed', _('Borrowed')
    LENT = 'lent', _('Lent')
    IN_PROGRESS = 'in_progress', _('In Progress')


class UserMedia(models.Model):
    """
    Links users to media in their collection with status and personal data.
    Changes to this model trigger Neo4j synchronization via signals.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='media_collection',
        verbose_name=_('user')
    )
    media = models.ForeignKey(
        Media,
        on_delete=models.CASCADE,
        related_name='user_collections',
        verbose_name=_('media')
    )
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=CollectionStatus.choices,
        db_index=True
    )
    rating = models.DecimalField(
        _('rating'),
        max_digits=3,
        decimal_places=1,
        null=True,
        blank=True,
        help_text=_('Rating from 0.0 to 10.0')
    )
    notes = models.TextField(
        _('notes'),
        blank=True,
        help_text=_('Private notes about this media')
    )

    # Timestamps
    added_at = models.DateTimeField(_('added at'), auto_now_add=True, db_index=True)
    completed_at = models.DateTimeField(
        _('completed at'),
        null=True,
        blank=True,
        help_text=_('When the user finished watching/reading/listening')
    )
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        db_table = 'collections_usermedia'
        verbose_name = _('user media')
        verbose_name_plural = _('user media')
        ordering = ['-added_at']
        unique_together = [['user', 'media', 'status']]
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['media']),
            models.Index(fields=['status']),
            models.Index(fields=['added_at']),
            models.Index(fields=['rating']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.media.title} ({self.get_status_display()})"

    def save(self, *args, **kwargs):
        """Override save to validate rating and trigger Neo4j sync."""
        # Validate rating
        if self.rating is not None and (self.rating < 0 or self.rating > 10):
            raise ValueError(_('Rating must be between 0.0 and 10.0'))

        super().save(*args, **kwargs)
        # Neo4j sync will be triggered by signal

    class ValidationError(Exception):
        """Custom validation error for rating."""
        pass
