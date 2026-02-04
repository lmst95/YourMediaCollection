from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

User = get_user_model()


class Note(models.Model):
    """Notes attached to books or documents"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notes'
    )

    # Generic relation to Book or Document
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    # Note content
    title = models.CharField(max_length=255, blank=True)
    content = models.TextField()

    # Metadata
    page_number = models.IntegerField(null=True, blank=True)  # Optional page reference
    is_public = models.BooleanField(default=False)  # For future friends feature

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['content_type', 'object_id']),
        ]

    def __str__(self):
        title = self.title or f"Notiz zu {self.content_object}"
        return f"{title} ({self.user.username})"
