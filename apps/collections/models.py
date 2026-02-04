"""
Collections models - UserMedia linking users to their media collections.
REDESIGNED: One media item per user with multiple property flags.
"""

import uuid
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from apps.media_catalog.models import Media


# Keep for backward compatibility with old code
class CollectionStatus(models.TextChoices):
    """DEPRECATED - kept for compatibility during migration."""
    OWNED = 'owned', _('Owned')
    WATCHED = 'watched', _('Watched')
    READ = 'read', _('Read')
    LISTENED = 'listened', _('Listened')
    WISHLIST = 'wishlist', _('Wishlist')
    BORROWED = 'borrowed', _('Borrowed')
    LENT = 'lent', _('Lent')
    IN_PROGRESS = 'in_progress', _('In Progress')


class UserMediaCollection(models.Model):
    """
    Core collection entry - ONE per user per media.
    Represents that a user has this media in their collection.
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

    # Core metadata
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

    # Property flags - can have multiple
    is_owned = models.BooleanField(_('owned'), default=False, db_index=True)
    is_wishlist = models.BooleanField(_('in wishlist'), default=False, db_index=True)
    is_watched = models.BooleanField(_('watched/read/listened'), default=False, db_index=True)
    is_in_progress = models.BooleanField(_('in progress'), default=False, db_index=True)

    # Timestamps
    added_at = models.DateTimeField(_('added to collection'), auto_now_add=True, db_index=True)
    watched_at = models.DateTimeField(
        _('watched/read/listened at'),
        null=True,
        blank=True,
        help_text=_('When the user finished this media')
    )
    updated_at = models.DateTimeField(_('updated at'), auto_now=True)

    class Meta:
        db_table = 'collections_usermedia_v2'
        verbose_name = _('user media collection')
        verbose_name_plural = _('user media collections')
        ordering = ['-added_at']
        unique_together = [['user', 'media']]  # Only ONE per user/media
        indexes = [
            models.Index(fields=['user', 'is_owned']),
            models.Index(fields=['user', 'is_wishlist']),
            models.Index(fields=['user', 'is_watched']),
            models.Index(fields=['user', 'is_in_progress']),
            models.Index(fields=['added_at']),
            models.Index(fields=['rating']),
        ]

    def __str__(self):
        flags = []
        if self.is_owned: flags.append('Owned')
        if self.is_wishlist: flags.append('Wishlist')
        if self.is_watched: flags.append('Watched')
        if self.is_in_progress: flags.append('In Progress')

        return f"{self.user.username} - {self.media.title} ({', '.join(flags) if flags else 'No flags'})"

    def save(self, *args, **kwargs):
        """Override save to validate rating."""
        if self.rating is not None and (self.rating < 0 or self.rating > 10):
            raise ValueError(_('Rating must be between 0.0 and 10.0'))
        super().save(*args, **kwargs)

    @property
    def status_flags(self):
        """Return list of active status flags."""
        flags = []
        if self.is_owned: flags.append('owned')
        if self.is_wishlist: flags.append('wishlist')
        if self.is_watched: flags.append('watched')
        if self.is_in_progress: flags.append('in_progress')
        return flags


class LendingRecord(models.Model):
    """
    Separate model for lending/borrowing tracking.
    Can have multiple lending records per media.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    collection_item = models.ForeignKey(
        UserMediaCollection,
        on_delete=models.CASCADE,
        related_name='lending_records'
    )

    # Lending type
    LENDING_TYPE_CHOICES = [
        ('lent', _('Lent to someone')),
        ('borrowed', _('Borrowed from someone')),
    ]
    lending_type = models.CharField(
        _('lending type'),
        max_length=10,
        choices=LENDING_TYPE_CHOICES
    )

    person_name = models.CharField(
        _('person name'),
        max_length=200,
        help_text=_('Who you lent to or borrowed from')
    )
    notes = models.TextField(_('notes'), blank=True)

    # Timestamps
    lent_at = models.DateTimeField(_('lent/borrowed at'), auto_now_add=True)
    returned_at = models.DateTimeField(_('returned at'), null=True, blank=True)
    is_returned = models.BooleanField(_('returned'), default=False)

    class Meta:
        db_table = 'collections_lending_record'
        verbose_name = _('lending record')
        verbose_name_plural = _('lending records')
        ordering = ['-lent_at']
        indexes = [
            models.Index(fields=['collection_item', 'is_returned']),
            models.Index(fields=['lending_type']),
        ]

    def __str__(self):
        status = "Returned" if self.is_returned else "Active"
        return f"{self.get_lending_type_display()}: {self.person_name} ({status})"


# Keep old model for migration compatibility
class UserMedia(models.Model):
    """
    OLD MODEL - Deprecated, kept for backward compatibility during migration.
    Will be removed after data migration.
    """

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='old_media_collection',
    )
    media = models.ForeignKey(
        Media,
        on_delete=models.CASCADE,
        related_name='old_user_collections',
    )
    status = models.CharField(max_length=20, db_index=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    notes = models.TextField(blank=True)
    added_at = models.DateTimeField(auto_now_add=True, db_index=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'collections_usermedia'
        managed = False  # Don't create/modify this table
