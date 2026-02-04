from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

User = get_user_model()


class Activity(models.Model):
    """Timeline/activity stream entries"""

    ACTIVITY_TYPES = [
        ('BOOK_ADDED', 'Buch zur Sammlung hinzugefügt'),
        ('BOOK_RATED', 'Buch bewertet'),
        ('DOCUMENT_UPLOADED', 'Dokument hochgeladen'),
        ('NOTE_CREATED', 'Notiz erstellt'),
        ('TODO_CREATED', 'Aufgabe erstellt'),
        ('TODO_COMPLETED', 'Aufgabe erledigt'),
        ('COLLECTION_CREATED', 'Sammlung erstellt'),
        ('STATUS_CHANGED', 'Status geändert'),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='activities'
    )

    # Activity metadata
    activity_type = models.CharField(max_length=30, choices=ACTIVITY_TYPES)
    description = models.TextField()

    # Generic relation to the object this activity is about
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey('content_type', 'object_id')

    # Additional context (JSON for flexibility)
    metadata = models.JSONField(default=dict, blank=True)

    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['activity_type', '-created_at']),
        ]
        verbose_name_plural = 'Activities'

    def __str__(self):
        return f"{self.user.username}: {self.get_activity_type_display()} ({self.created_at.strftime('%d.%m.%Y %H:%M')})"
