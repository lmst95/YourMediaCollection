"""
Models for data_sync app - tracking external API synchronization.
"""

import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _


class SyncTask(models.Model):
    """Track external API sync tasks."""

    SYNC_STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('running', _('Running')),
        ('completed', _('Completed')),
        ('failed', _('Failed')),
    ]

    SOURCE_CHOICES = [
        ('tmdb', _('TMDb')),
        ('openlibrary', _('Open Library')),
        ('musicbrainz', _('MusicBrainz')),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source = models.CharField(_('source'), max_length=50, choices=SOURCE_CHOICES)
    media_type = models.CharField(_('media type'), max_length=20, blank=True)
    last_sync_at = models.DateTimeField(_('last sync at'), null=True, blank=True)
    next_sync_at = models.DateTimeField(_('next sync at'), null=True, blank=True)
    status = models.CharField(
        _('status'),
        max_length=20,
        choices=SYNC_STATUS_CHOICES,
        default='pending'
    )
    records_processed = models.IntegerField(_('records processed'), default=0)
    errors = models.JSONField(_('errors'), default=list, blank=True)
    created_at = models.DateTimeField(_('created at'), auto_now_add=True)

    class Meta:
        db_table = 'data_sync_synctask'
        verbose_name = _('sync task')
        verbose_name_plural = _('sync tasks')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.get_source_display()} - {self.get_status_display()}"
